
from __future__ import annotations

import json
import re
import uuid
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import os
import hmac
import hashlib
import base64
import time
import threading

from collections import defaultdict
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException, Query
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field

from crop_guardian_engine import run_crop_guardian
from crop_guardian_reports import (
    load_diagnosis_history,
    build_diagnosis_pdf,
)

BASE_DIR = Path(__file__).resolve().parent
EVAL_DIR = BASE_DIR / "eval"
DATA_DIR = BASE_DIR / "data"
# --------------------------------------------------
# PUBLIC TESTER SECURITY
# --------------------------------------------------

load_dotenv(BASE_DIR / ".env")

TESTER_ACCESS_CODE = os.getenv("TESTER_ACCESS_CODE", "")
TESTER_TOKEN_SECRET = os.getenv("TESTER_TOKEN_SECRET", "")

TOKEN_LIFETIME = 12 * 60 * 60

_login_attempts = defaultdict(list)
_diagnosis_attempts = defaultdict(list)
_rate_lock = threading.Lock()

HISTORY_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,180}$")

SUPPORTED_CROPS = {
    "potato", "tomato", "rice", "brinjal", "jute"
}

CLASSIFIER_CROPS = {"potato", "tomato"}

# --------------------------------------------------
# TESTER AUTHENTICATION
# --------------------------------------------------

def create_tester_token():
    expires = int(time.time()) + TOKEN_LIFETIME

    payload = {
        "role": "tester",
        "exp": expires,
    }

    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode().rstrip("=")

    signature = hmac.new(
        TESTER_TOKEN_SECRET.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{encoded}.{signature}"


def validate_tester_token(token):
    try:
        encoded, supplied_signature = token.split(".", 1)

        expected_signature = hmac.new(
            TESTER_TOKEN_SECRET.encode(),
            encoded.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            supplied_signature, expected_signature
        ):
            return False

        padding = "=" * (-len(encoded) % 4)

        payload = json.loads(
            base64.urlsafe_b64decode(encoded + padding)
        )

        return (
            payload.get("role") == "tester"
            and int(payload.get("exp", 0)) > int(time.time())
        )

    except Exception:
        return False

def get_client_ip(request):
    return (
        request.headers.get("cf-connecting-ip")
        or (request.client.host if request.client else "unknown")
    )
def check_rate_limit(store, key, maximum, window):
    now = time.monotonic()

    with _rate_lock:
        attempts = [
            stamp for stamp in store[key]
            if now - stamp < window
        ]

        if len(attempts) >= maximum:
            store[key] = attempts
            return False

        attempts.append(now)
        store[key] = attempts
        return True


class TesterLogin(BaseModel):
    access_code: str


app = FastAPI(
    title="Crop Guardian API",
    description="API for the Crop Guardian agricultural assistant.",
    version="1.0.0",
)


@app.post("/api/auth/login")
def tester_login(data: TesterLogin, request: Request):

    ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(
        _login_attempts, ip, 10, 900
    ):
        raise HTTPException(429, "Too many login attempts.")

    if not TESTER_ACCESS_CODE or not TESTER_TOKEN_SECRET:
        raise HTTPException(
            503, "Tester authentication is not configured."
        )

    if not hmac.compare_digest(
        data.access_code,
        TESTER_ACCESS_CODE
    ):
        raise HTTPException(401, "Invalid tester access code.")

    return {
        "access_token": create_tester_token(),
        "token_type": "bearer",
        "expires_in": TOKEN_LIFETIME,
    }


# --------------------------------------------------
# PROTECT PRIVATE API ROUTES
# --------------------------------------------------


@app.middleware("http")
async def public_api_protection(request: Request, call_next):
    path = request.url.path

    # Reject oversized requests.
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 13 * 1024 * 1024:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request exceeds upload limit."},
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid content length."},
            )

    # Public diagnosis rate limit.
    if path == "/api/diagnose" and request.method == "POST":
        ip = get_client_ip(request)

        if not check_rate_limit(
            _diagnosis_attempts, ip, 5, 600
        ):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Diagnosis limit reached. Try again later."
                },
            )

    return await call_next(request)





app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --------------------------------------------------
# GENERAL HELPERS
# --------------------------------------------------

def read_json(path: Path, default=None):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_location():
    return read_json(
        DATA_DIR / "weather_location.json",
        {
            "latitude": 23.8103,
            "longitude": 90.4125,
            "source": "default_dhaka",
        },
    )


def validate_location(latitude, longitude):
    if not (-90 <= latitude <= 90):
        raise HTTPException(400, "Invalid latitude.")

    if not (-180 <= longitude <= 180):
        raise HTTPException(400, "Invalid longitude.")



def safe_report_path(report_id: str) -> Path:
    if not HISTORY_ID_PATTERN.fullmatch(report_id):
        raise HTTPException(400, "Invalid report ID.")

    matches = [
        EVAL_DIR / f"{report_id}.json",
        EVAL_DIR / f"{report_id}_report.json",
    ]

    for path in matches:
        if path.is_file():
            return path.resolve()

    raise HTTPException(404, "Report not found.")


def get_disease_name(report):
    diagnosis = report.get("diagnosis", {})
    predictions = diagnosis.get("model_predictions", [])

    if not predictions:
        return None

    names = [
        str(p.get("disease", "")).strip()
        for p in predictions
        if p.get("disease")
        and str(p.get("disease")).lower() not in {"healthy", "unknown"}
    ]

    if not names:
        return "Healthy"

    normalized = {x.lower().replace("_", " ") for x in names}

    if len(normalized) == 1:
        return names[0].replace("_", " ").title()

    return None


def disease_id(crop, disease):
    value = f"{crop}-{disease}".lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")

def extract_knowledge_sections(diagnosis):
    result = {
        "symptoms": [],
        "causes": [],
        "actions": [],
        "prevention": [],
        "chemical_options": [],
        "sources": [],
    }

    labels = {
        "Symptoms": "symptoms",
        "Early signs": "symptoms",
        "Favorable conditions": "causes",
        "Low-cost actions": "actions",
        "Chemical options": "chemical_options",
"Prevention": "prevention",
    }

    seen = set()

    for retrieval in diagnosis.get("knowledge_retrieval", []) or []:
        for match in retrieval.get("knowledge", []) or []:

            document = match.get("document", "")

            if not isinstance(document, str):
                continue

            extracted = {}

            current = None

            for line in document.splitlines():
                line = line.strip()

                if ":" in line:
                    label, value = line.split(":", 1)
                    label = label.strip()

                    if label in labels:
                        current = labels[label]
                        extracted.setdefault(current, [])
                        if value.strip():
                            extracted[current].append(value.strip())
                        continue

                if current and line:
                    extracted[current].append(line)

            for key, values in extracted.items():
                for value in values:
                    for item in value.split(";"):
                        item = item.strip()
                        if item and (key, item) not in seen:
                            result[key].append(item)
                            seen.add((key, item))

            if match.get("source_name"):
                result["sources"].append({
                    "name": match["source_name"],
                    "url": match.get("source_url", ""),
                    "verification": match.get(
                        "verification_status", "unverified"
                    ),
                })

    return result


def plain_diagnosis(report, lang="en"):
    diagnosis = report.get("diagnosis", {}) or {}
    weather = report.get("weather_intelligence", {}) or {}
    safety = report.get("safety", {}) or {}

    predictions = diagnosis.get("model_predictions", []) or []

    names = [
        str(item.get("disease", "")).replace("_", " ")
        for item in predictions
        if item.get("disease")
    ]

    unique_names = list(dict.fromkeys(names))
    disease = get_disease_name(report)

    needs_review = bool(
        safety.get(
            "human_review_required",
            diagnosis.get("needs_review", True),
        )
    )

    if disease == "Healthy":
        status = "likely_identified" if not needs_review else "needs_checking"
        is_healthy = True
    elif disease and not needs_review and len(unique_names) == 1:
        status = "likely_identified"
        is_healthy = False
    elif disease:
        status = "needs_checking"
        is_healthy = False
    else:
        status = "unable_to_identify"
        is_healthy = False

    knowledge = diagnosis.get("knowledge_retrieval", []) or []
    knowledge_sections = extract_knowledge_sections(diagnosis)
    verified = (
        bool(diagnosis.get("farmer_guidance_allowed", False))
        and not needs_review
    )

    # Only expose information from the existing knowledge results.
    # Do not manufacture pesticide recommendations.
    documents = []
    for retrieval in knowledge:
        for match in retrieval.get("knowledge", []) or []:
            if verified and match.get("verification_status") == "verified":
                documents.append({
                    "text": match.get("document", ""),
                    "source": match.get("source_name", ""),
                    "sourceUrl": match.get("source_url", ""),
                })

    alerts = weather.get("crop_weather_context", []) or []
    weather_messages = []

    for alert in alerts:
        key = "message_bn" if lang == "bn" else "message_en"
        message = alert.get(key)
        if message:
            weather_messages.append(message)

    crop = report.get("selected_crop", "unknown")

    summary = diagnosis.get("final_message") or (
        "The photograph could not be assessed reliably."
        if lang == "en"
        else "ছবিটি নির্ভরযোগ্যভাবে পরীক্ষা করা যায়নি।"
    )

    return {
        "id": report.get("_api_id", ""),
        "createdAt": report.get("_created_at", datetime.now(timezone.utc).isoformat()),
        "lang": lang,
        "crop": crop,
        "status": status,
        "disease": {
            "id": disease_id(crop, disease or "unknown"),
            "name": disease or "Unable to identify",
            "isHealthy": is_healthy,
        },
        "summary": summary,
        "symptoms": knowledge_sections["symptoms"],
"causes": knowledge_sections["causes"],
"actions": knowledge_sections["actions"],
        "treatment": {
            "verified": verified and bool(documents),
            "products": [],
            "verifiedInformation": documents,
        },
      "prevention": knowledge_sections["prevention"],
        "weather": {
            "summary": " ".join(weather_messages),
            "points": [],
        },
        "imageUrl": (
    f"/api/history/{report.get('_api_id')}/image"
    if report.get("_image_filename")
    else None
),
        "technical": {
            "model_predictions": predictions,
            "hybrid_status": diagnosis.get("hybrid_status"),
            "needs_review": needs_review,
            "weather_location": weather.get("location"),
            "warnings": diagnosis.get("warnings", []),
        },
    }


def load_saved_report(report_id):
    path = safe_report_path(report_id)
    report = read_json(path)

    if not isinstance(report, dict):
        raise HTTPException(500, "Saved report is invalid.")

    return report


def report_identifier(path):
    return path.stem


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "Crop Guardian API",
        "version": "1.0.0",
    }


# --------------------------------------------------
# DIAGNOSIS
# --------------------------------------------------

@app.post("/api/diagnose")
async def diagnose(
    image: UploadFile = File(...),
    crop: str = Form(...),
    lang: str = Form("en"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
):
    crop = crop.lower().strip()
    lang = lang.lower().strip()

    if crop not in SUPPORTED_CROPS:
        raise HTTPException(400, "Unsupported crop.")

    if lang not in {"en", "bn"}:
        lang = "en"

    if (latitude is None) != (longitude is None):
        raise HTTPException(
            400, "Latitude and longitude must be supplied together."
        )

    if latitude is not None:
        validate_location(latitude, longitude)
        coordinates = {
            "latitude": latitude,
            "longitude": longitude,
            "source": "farmer_selected_field",
        }
    else:
        coordinates = get_location()

    suffix = Path(image.filename or "").suffix.lower()

    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(400, "Upload a JPG, PNG or WEBP image.")

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(400, "The uploaded image is empty.")

    if len(image_bytes) > 12 * 1024 * 1024:
        raise HTTPException(413, "Image must be smaller than 12 MB.")

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=str(DATA_DIR),
        ) as temp:
            temp.write(image_bytes)
            temp_path = Path(temp.name)


        # Existing engine runs in FastAPI's synchronous worker thread.
        report = run_crop_guardian(
            temp_path,
            crop,
            original_filename=Path(image.filename).name,
            field_coordinates=coordinates,
            save_report=False,
        )




        # Detect temporary Gemini service outages.
        diagnosis = report.get("diagnosis", {}) or {}
        warnings = diagnosis.get("warnings", []) or []

        gemini_unavailable = (
            diagnosis.get("hybrid_status") == "validation_failed"
            and any(
                "503 UNAVAILABLE" in str(warning)
                for warning in warnings
            )
        )

        if gemini_unavailable:
            # Do not retain an incomplete examination as a diagnosis.


            raise HTTPException(
                status_code=503,
                detail={
                    "code": "AI_SERVICE_UNAVAILABLE",
                    "message": (
                        "Our examination service is temporarily busy. "
                        "Please try again shortly."
                    ),
                    "retryable": True,
                },
            )




        report_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # Permanently preserve the farmer's original photograph.
        image_dir = DATA_DIR / "diagnosis_images"
        image_dir.mkdir(parents=True, exist_ok=True)

        image_filename = f"{report_id}{suffix}"
        permanent_image_path = image_dir / image_filename

        shutil.copy2(temp_path, permanent_image_path)

        report["_api_id"] = report_id
        report["_created_at"] = created_at
        report["_language"] = lang
        report["_image_filename"] = image_filename

        # Save a stable API history record separately.

        history_path = EVAL_DIR / f"{report_id}_report.json"
        write_json(history_path, report)

        return plain_diagnosis(report, lang)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            500,
            f"Diagnosis failed: {str(exc)}",
        ) from exc
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)


# --------------------------------------------------
# WEATHER
# --------------------------------------------------


@app.get("/api/weather")
def get_weather(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    crop: Optional[str] = None,
    lang: str = "en",
):
    import csv
    from datetime import datetime, timezone, timedelta

    location = get_location()

    if latitude is not None or longitude is not None:
        if latitude is None or longitude is None:
            raise HTTPException(400, "Both coordinates are required.")
        validate_location(latitude, longitude)
        location = {"latitude": latitude, "longitude": longitude}

    risk = read_json(
        EVAL_DIR / "bangladesh_weather_risk.json", {}
    )
    alerts = read_json(
        EVAL_DIR / "weather_alerts.json", {}
    )

    alert_list = alerts.get("alerts", [])

    if crop:
        alert_list = [
            item for item in alert_list
            if str(item.get("crop", "")).lower() == crop.lower()
        ]

    def number(value):
        try:
            result = float(value)
            if result == -999:
                return None
            return result
        except (TypeError, ValueError):
            return None

    # -----------------------------
    # DAILY WEATHER
    # -----------------------------

    daily = []
    daily_path = DATA_DIR / "weather_daily.csv"

    if daily_path.exists():
        with daily_path.open(
            encoding="utf-8", newline=""
        ) as handle:
            records = list(csv.DictReader(handle))

        for record in records[-7:]:
            try:
                date_value = datetime.strptime(
                    record["date"], "%Y%m%d"
                ).date().isoformat()
            except (ValueError, KeyError):
                continue

            daily.append({
                "date": date_value,
                "temperatureC": number(record.get("T2M_C")),
                "humidityPct": number(record.get("RH2M_percent")),
                "rainfallMm": number(record.get("PRECTOTCORR_mm_day")),
            })

    # -----------------------------
    # HOURLY WEATHER
    # -----------------------------

    hourly_path = DATA_DIR / "weather_hourly.csv"
    latest = None
    observed_at = None
    is_fresh = False

    if hourly_path.exists():
        with hourly_path.open(
            encoding="utf-8", newline=""
        ) as handle:
            records = list(csv.DictReader(handle))

        valid_records = []

        for record in records:
            try:
                timestamp = datetime.strptime(
                    record["datetime_utc"], "%Y%m%d%H"
                ).replace(tzinfo=timezone.utc)

                valid_records.append((timestamp, record))
            except (ValueError, KeyError):
                continue

        if valid_records:
            timestamp, latest = max(
                valid_records, key=lambda item: item[0]
            )

            observed_at = timestamp.isoformat()

            age = datetime.now(timezone.utc) - timestamp

            is_fresh = timedelta(0) <= age <= timedelta(hours=36)

    if latest:
        observation = {
            "temperatureC": number(latest.get("T2M_C")),
            "humidityPct": number(latest.get("RH2M_percent")),
            "rainfallMm": number(latest.get("PRECTOTCORR_mm_hour")),
            "observedAt": observed_at,
            "periodLabel": (
                f"Latest observation: "
                f"{timestamp.strftime('%d %b %Y, %H:%M UTC')}"
            ),
            "isFresh": is_fresh,
            "freshnessMessage": (
                "Latest hourly observation is available."
                if is_fresh
                else (
                    "Weather observations are outdated. "
                    "Please update weather data."
                    if lang != "bn"
                    else "আবহাওয়ার তথ্য পুরোনো। অনুগ্রহ করে আপডেট করুন।"
                )
            ),
        }
    else:
        observation = {
            "temperatureC": None,
            "humidityPct": None,
            "rainfallMm": None,
            "observedAt": None,
            "periodLabel": "No hourly observation available.",
            "isFresh": False,
            "freshnessMessage": (
                "No hourly weather data is available."
                if lang != "bn"
                else "কোনো ঘণ্টাভিত্তিক আবহাওয়ার তথ্য পাওয়া যায়নি।"
            ),
        }

    return {
        "location": {
            "label": "Selected field",
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
        },
        "observation": observation,
        "daily": daily,
        "cropContext": [
            item.get(
                "message_bn" if lang == "bn" else "message_en", ""
            )
            for item in alert_list
        ],
        "guidance": risk.get("limitations", []),
        "source": alerts.get("data_source", "NASA POWER"),
        "note": "Weather observations are contextual and do not confirm disease.",
    }


class FieldLocation(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


@app.post("/api/weather/update")
def update_weather(location: FieldLocation):
    latitude = location.latitude
    longitude = location.longitude

    try:
        import weather as daily_weather
        import weather_hourly as hourly_weather
        import bangladesh_weather_risk as risk_engine
        import weather_alerts

        start_date, end_date = daily_weather.get_default_dates()
        daily_payload = daily_weather.fetch_weather(
            latitude, longitude, start_date, end_date
        )
        daily_records = daily_weather.process_weather(daily_payload)

        if not daily_records:
            raise RuntimeError("No daily weather records returned.")

        daily_weather.save_weather(
            daily_records, latitude, longitude
        )

        hourly_payload, _, _ = hourly_weather.fetch_hourly(
            latitude, longitude
        )
        hourly_records = hourly_weather.process_hourly(hourly_payload)

        if not hourly_records:
            raise RuntimeError("No hourly weather records returned.")

        hourly_weather.save_hourly(hourly_records)

        write_json(
            DATA_DIR / "weather_location.json",
            {
                "latitude": latitude,
                "longitude": longitude,
                "source": "farmer_selected_field",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        risk_engine.main(latitude, longitude)
        weather_alerts.main()

        return {
            "latitude": latitude,
            "longitude": longitude,
            "source": "farmer_selected_field",
            "message": "Weather updated successfully.",
        }

    except Exception as exc:
        raise HTTPException(
            502, f"Weather update failed: {exc}"
        ) from exc


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

@app.get("/api/history")
def history(
    crop: Optional[str] = None,
    q: Optional[str] = None,
    lang: str = "en",
):
    results = []

    for entry in load_diagnosis_history():
        report = entry["report"]
        report_id = report.get("_api_id")

        if not report_id:
            # Legacy Streamlit reports are still readable.
            report_id = entry["path"].stem

        if crop and entry["crop"] != crop.lower():
            continue

        if q and q.lower() not in (
            entry["image"] + " " + entry["crop"]
        ).lower():
            continue

        mapped = plain_diagnosis(report, lang)
        results.append({
            "id": report_id,
            "createdAt": entry["modified"].isoformat(),
            "crop": entry["crop"],
            "status": mapped["status"],
            "diseaseName": mapped["disease"]["name"],
            "isHealthy": mapped["disease"]["isHealthy"],
            "thumbUrl": None,
        })
    return results

@app.get("/api/history/{report_id}/image")
def history_image(report_id: str):
    report = load_saved_report(report_id)

    filename = report.get("_image_filename")

    if not filename:
        raise HTTPException(404, "Original plant image not available.")

    # Only allow filenames belonging to this report ID.
    if filename not in {
        f"{report_id}.jpg",
        f"{report_id}.jpeg",
        f"{report_id}.png",
        f"{report_id}.webp",
    }:
        raise HTTPException(404, "Invalid image reference.")

    image_path = DATA_DIR / "diagnosis_images" / filename

    if not image_path.is_file():
        raise HTTPException(404, "Plant image not found.")

    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }

    return FileResponse(
        image_path,
        media_type=media_types[image_path.suffix.lower()],
    )
@app.get("/api/history/{report_id}")
def history_detail(report_id: str, lang: str = "en"):
    report = load_saved_report(report_id)
    return plain_diagnosis(report, lang)


@app.get("/api/history/{report_id}/pdf")
def history_pdf(report_id: str):
    report = load_saved_report(report_id)
    lang = report.get("_language", "en")

    try:
        pdf_bytes = build_diagnosis_pdf(report, lang)
    except Exception as exc:
        raise HTTPException(500, f"PDF generation failed: {exc}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="crop_guardian_{report_id}.pdf"'
        },
    )


# --------------------------------------------------
# DISEASE GUIDE
# --------------------------------------------------

def load_disease_entries():
    path = BASE_DIR / "knowledge" / "disease_knowledge.json"
    data = read_json(path, [])

    if not isinstance(data, list):
        return []

    return data



@app.get("/api/diseases")
def diseases(
    crop: Optional[str] = None,
    q: Optional[str] = None,
    lang: str = "en",
):
    output = []
    seen = set()

    for item in load_disease_entries():
        item_crop = str(item.get("crop", "")).lower()
        name = str(item.get("disease", ""))
        healthy = name.lower() == "healthy"

        if crop and item_crop != crop.lower():
            continue

        if q and q.lower() not in (name + " " + item_crop).lower():
            continue

        key = (item_crop, name.lower())
        if key in seen:
            continue
        seen.add(key)

        early_signs = item.get("early_signs", [])
        symptoms = item.get("symptoms", [])

        output.append({
            "id": disease_id(item_crop, name),
            "crop": item_crop,
            "name": name.replace("_", " ").title(),
            "isHealthy": healthy,
            "blurb": (
                early_signs[0]
                if early_signs
                else (symptoms[0] if symptoms else "")
            ),
        })

    return output


@app.get("/api/diseases/{item_id}")
def disease_detail(item_id: str, lang: str = "en"):
    for item in load_disease_entries():
        current_id = disease_id(
            str(item.get("crop", "")),
            str(item.get("disease", "")),
        )

        if current_id == item_id:
            healthy = str(item.get("disease", "")).lower() == "healthy"

            return {
                "id": current_id,
                "crop": item.get("crop"),
                "name": str(item.get("disease", "")).replace("_", " ").title(),
                "isHealthy": healthy,
                "blurb": "",
                "overview": (
                    f"Scientific name: {item.get('scientific_name')}"
                    if item.get("scientific_name")
                    else ""
                ),
                "symptoms": item.get("symptoms", []),
                "causes": item.get("favorable_conditions", []),
                "prevention": [],
                "management": item.get("low_cost_actions", []),
                "treatment": {
                    "verified": False,
                    "products": [],
                },
            }

    raise HTTPException(404, "Disease information not found.")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
