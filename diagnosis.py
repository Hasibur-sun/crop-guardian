
import os
import io
import json
import time
import hashlib
import sys
from pathlib import Path
from typing import List, Literal

from dotenv import load_dotenv
from PIL import Image, ImageOps
from pydantic import BaseModel, Field
from google import genai
from google.genai import types


# =====================================
# 1. PROJECT CONFIGURATION
# =====================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

MODEL = "gemini-3.5-flash-lite"
PROMPT_VERSION = "crop-guardian-day1-v2"

CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)


# =====================================
# 2. ALLOWED DISEASES AND CROPS
# =====================================

CropName = Literal[
    "potato", "tomato", "rice",
    "brinjal", "jute", "other", "unknown"
]

DiseaseName = Literal[
    "Late blight",
    "Early blight",
    "Bacterial spot",
    "Leaf mold",
    "Septoria leaf spot",
    "Blast",
    "Brown spot",
    "Bacterial leaf blight",
    "Powdery mildew",
    "Healthy",
    "Unknown"
]


# =====================================
# 3. JSON RESPONSE STRUCTURE
# =====================================

class Candidate(BaseModel):
    disease: DiseaseName
    confidence: float = Field(ge=0.0, le=1.0)


class Diagnosis(BaseModel):
    is_plant_photo: bool
    crop: CropName
    healthy: bool
    top3: List[Candidate]
    symptoms_seen: List[str]
    photo_quality: Literal[
        "good", "blurry", "dark", "too_far", "other"
    ]


# =====================================
# 4. GEMINI PROMPT
# =====================================

PROMPT = """
You are a careful plant pathology assistant
for smallholder farmers in Bangladesh.

Analyze the uploaded image and return the required JSON.

GENERAL RULES:

1. If the image does not show a crop plant or leaf:
   is_plant_photo=false
   crop="unknown"
   healthy=false
   top3=[]
   symptoms_seen=[]

2. Crop must be one of:
   potato, tomato, rice, brinjal, jute, other, unknown.

3. Return up to 3 possible conditions, most likely first.

4. Only use these disease names:
   Late blight, Early blight, Bacterial spot,
   Leaf mold, Septoria leaf spot, Blast,
   Brown spot, Bacterial leaf blight,
   Powdery mildew, Healthy, Unknown.

5. Confidence values must be between 0 and 1.
   Their sum must not exceed 1.

6. Never give confidence above 0.90.

7. Use confidence >= 0.85 only when symptoms
   are textbook-clear and the image is sharp.

8. If two diseases look similar, distribute
   confidence between the alternatives.

9. healthy=true only when Healthy is the
   most likely condition.

10. Describe only visible symptoms.

11. Do not provide treatment advice.

PHOTO QUALITY:

12. Use only:
    good, blurry, dark, too_far, other.

13. If lesion boundaries and leaf details
    cannot be clearly seen, classify as blurry.

14. If the image is dim, classify as dark.

15. If the leaf is too small in the frame,
    classify as too_far.

16. If photo_quality is not good, the highest
    confidence must not exceed 0.50.

17. If crop is other or unknown, the highest
    confidence must not exceed 0.50.

DISEASE DIFFERENTIATION:

18. Potato early blight:
    Brown lesions with concentric target-like rings,
    often on older lower leaves.

19. Potato late blight:
    Irregular water-soaked, greasy dark lesions.
    White fuzzy growth may appear underneath.

20. Rice blast:
    Spindle-shaped or diamond-shaped lesions
    with gray or whitish centers and darker margins.

21. Rice brown spot:
    Small round-to-oval brown lesions,
    sometimes with yellow halos.

22. Tomato leaf mold:
    Yellowish patches on the upper leaf surface.
    Olive-green or grayish fuzzy growth may appear
    on the underside.
    If underside is unavailable, express uncertainty.

23. Early blight and late blight must not be
    confused simply because both have brown lesions.

24. Do not diagnose a disease solely from
    the background or image filename.

25. If evidence is insufficient, use Unknown
    rather than forcing a diagnosis.

26. Focus on the leaf and ignore the background.
27. IMPORTANT POTATO DIFFERENTIATION:
    Do not classify a potato leaf as Late blight
    simply because brown or necrotic lesions are visible.

28. If multiple discrete brown lesions show
    concentric target-like rings, prefer Early blight.

29. Late blight should be preferred when there
    is convincing evidence of irregular,
    water-soaked expanding lesions.

30. Do not invent water-soaked symptoms.
    Only report them when clearly visible.

31. If the distinction between Early blight
    and Late blight is uncertain, distribute
    confidence between both candidates.
"""


# =====================================
# 5. IMAGE PREPARATION
# =====================================

def prepare_image(path: str) -> bytes:

    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img).convert("RGB")

    except Exception as e:
        raise ValueError(f"Cannot open image: {e}")

    img.thumbnail((1024, 1024))

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)

    return buffer.getvalue()


# =====================================
# 6. RESULT VALIDATION AND SAFETY
# =====================================

def enforce_rules(result: dict) -> dict:

    # Reject non-plant images consistently
    if not result["is_plant_photo"]:

        result["crop"] = "unknown"
        result["healthy"] = False
        result["top3"] = []
        result["symptoms_seen"] = []
        result["photo_quality"] = "other"

        return result

    # Never return more than three candidates
    result["top3"] = result["top3"][:3]

    # Clamp confidence values
    for candidate in result["top3"]:
        candidate["confidence"] = max(
            0.0,
            min(1.0, float(candidate["confidence"]))
        )

    # Confidence must add up to 1 or less
    total = sum(
        c["confidence"] for c in result["top3"]
    )

    if total > 1.0:
        for candidate in result["top3"]:
            candidate["confidence"] /= total

    # Enforce conservative confidence for poor images
    if (
        result["photo_quality"] != "good"
        or result["crop"] in ("other", "unknown")
    ):

        if result["top3"]:

            top = result["top3"][0]

            if top["confidence"] > 0.50:

                top["confidence"] = 0.50

                remaining = result["top3"][1:]

                remaining_total = sum(
                    c["confidence"] for c in remaining
                )

                if remaining_total > 0.50:

                    for c in remaining:
                        c["confidence"] *= (
                            0.50 / remaining_total
                        )

    # Derive healthy from the highest-ranked candidate
    result["healthy"] = (
        bool(result["top3"])
        and result["top3"][0]["disease"] == "Healthy"
    )

    return result


# =====================================
# 7. MAIN DIAGNOSIS FUNCTION
# =====================================

def diagnose(path: str, use_cache: bool = True) -> dict:

    jpeg = prepare_image(path)

    # Include prompt version in cache key.
    # New prompt = fresh diagnosis.
    cache_input = (
        jpeg + PROMPT.encode("utf-8")
        + PROMPT_VERSION.encode("utf-8")
    )

    image_hash = hashlib.sha256(
        cache_input
    ).hexdigest()

    cache_file = CACHE_DIR / f"{image_hash}.json"

    if use_cache and cache_file.exists():

        print("Using cached result...")

        return json.loads(
            cache_file.read_text(encoding="utf-8")
        )

    image_part = types.Part.from_bytes(
        data=jpeg,
        mime_type="image/jpeg"
    )

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Diagnosis,
        temperature=0.2
    )

    last_error = None

    for attempt in range(3):

        try:

            print("Sending image to Gemini...")

            response = client.models.generate_content(
                model=MODEL,
                contents=[image_part, PROMPT],
                config=config
            )

            if not response.text:
                raise ValueError("Empty Gemini response.")

            diagnosis = Diagnosis.model_validate_json(
                response.text
            )

            result = enforce_rules(
                diagnosis.model_dump()
            )

            cache_file.write_text(
                json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )

            return result

        except Exception as e:

            last_error = e

            print(
                f"Attempt {attempt + 1} failed: {e}"
            )

            if attempt < 2:
                time.sleep(3 * (2 ** attempt))

    raise RuntimeError(
        f"Diagnosis failed after 3 attempts: {last_error}"
    )


# =====================================
# 8. RUN FROM TERMINAL
# =====================================

if __name__ == "__main__":

    if len(sys.argv) < 2:

        print("Usage: python diagnosis.py image_path")
        sys.exit(1)

    try:

        result = diagnose(sys.argv[1])

        print("\n========== CROP GUARDIAN ==========")

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

        print("===================================")

    except Exception as e:

        print(f"\nERROR: {e}")
        sys.exit(1)
