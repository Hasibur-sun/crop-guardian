
import json
from pathlib import Path

from hybrid_rag import diagnose_with_knowledge


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

WEATHER_ALERT_FILE = (
    BASE_DIR / "eval" / "weather_alerts.json"
)

OUTPUT_DIR = BASE_DIR / "eval"

OUTPUT_FILE = (
    OUTPUT_DIR / "crop_guardian_final_report.json"
)


# ==========================================
# 2. NORMALIZE NAMES
# ==========================================

def normalize(value):

    return (
        str(value or "")
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .strip()
    )


# ==========================================
# 3. LOAD WEATHER ALERTS
# ==========================================

def load_weather_alerts():

    if not WEATHER_ALERT_FILE.exists():

        raise FileNotFoundError(
            "Weather alerts not found. "
            "Run weather_alerts.py first."
        )

    with open(
        WEATHER_ALERT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================================
# 4. MATCH WEATHER ALERTS
# ==========================================

def match_weather(
    selected_crop,
    predictions,
    weather_data
):

    alerts = weather_data.get("alerts", [])

    # Find weather context for selected crop

    crop_alerts = [

        alert for alert in alerts

        if normalize(alert.get("crop"))
        == normalize(selected_crop)
    ]

    disease_matches = []

    for prediction in predictions:

        predicted_crop = prediction.get("crop")

        predicted_disease = prediction.get("disease")

        if normalize(predicted_crop) != normalize(selected_crop):
            continue

        if normalize(predicted_disease) in {
            "healthy",
            "unknown"
        }:
            continue

        for alert in crop_alerts:

            if (
                normalize(alert.get("disease"))
                == normalize(predicted_disease)
            ):

                disease_matches.append({

                    "predicted_disease": predicted_disease,

                    "predicted_by": prediction.get(
                        "source_model"
                    ),

                    "weather_alert": alert

                })

    return {

        "selected_crop": selected_crop,

        "crop_weather_context": crop_alerts,

        "disease_specific_matches": disease_matches,

        "weather_disease_match_found": (
            len(disease_matches) > 0
        )
    }


# ==========================================
# 5. UNIFIED CROP GUARDIAN ENGINE
# ==========================================

def run_crop_guardian(
    image_path,
    selected_crop
):

    selected_crop = selected_crop.lower().strip()

    print("\n========== CROP GUARDIAN ==========")

    # --------------------------------------
    # A. IMAGE DIAGNOSIS + RAG
    # --------------------------------------

    print("\nStep 1: Running hybrid diagnosis and RAG...")

    diagnosis = diagnose_with_knowledge(
        image_path,
        selected_crop
    )

    if not isinstance(diagnosis, dict):

        raise TypeError(
            "Hybrid diagnosis did not return a dictionary."
        )

    # --------------------------------------
    # B. LOAD WEATHER ALERTS
    # --------------------------------------

    print("\nStep 2: Loading weather intelligence...")

    weather_data = load_weather_alerts()

    # --------------------------------------
    # C. MATCH DISEASE AND WEATHER
    # --------------------------------------

    print("\nStep 3: Matching weather context...")

    predictions = diagnosis.get(
        "model_predictions", []
    )

    weather_result = match_weather(
        selected_crop,
        predictions,
        weather_data
    )

    # --------------------------------------
    # D. BUILD FINAL REPORT
    # --------------------------------------

    final_report = {

        "project": "Crop Guardian",

        "image": diagnosis.get("image"),

        "selected_crop": selected_crop,

        "diagnosis": diagnosis,

        "weather_intelligence": {

            "data_source": weather_data.get(
                "data_source"
            ),

            "location": weather_data.get(
                "location"
            ),

            "crop_weather_context": (
                weather_result["crop_weather_context"]
            ),

            "disease_specific_matches": (
                weather_result["disease_specific_matches"]
            ),

            "weather_disease_match_found": (
                weather_result["weather_disease_match_found"]
            )
        },

        "safety": {

            "image_diagnosis_is_confirmed": False,

            "weather_confirms_disease": False,

            "weather_location_is_farm_verified": False,

            "farmer_guidance_allowed": (
                diagnosis.get(
                    "farmer_guidance_allowed",
                    False
                )
            ),

            "human_review_required": (
                diagnosis.get("needs_review", True)
            ),

            "disclaimer": (
                "Weather indicators do not confirm disease "
                "infection. NASA POWER provides gridded "
                "weather estimates. The configured Dhaka "
                "coordinates may not represent the farmer's "
                "actual field. Consult an agricultural officer "
                "when symptoms or uncertainty are present."
            )
        }
    }

    # --------------------------------------
    # E. SAVE REPORT
    # --------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report_file = (
    OUTPUT_DIR /
    f"{Path(image_path).stem}_{selected_crop}_report.json"
)

    with open(
    report_file,
    "w",
    encoding="utf-8"
) as f:

        json.dump(
            final_report,
            f,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------
    # F. DISPLAY SUMMARY
    # --------------------------------------

    print("\n========== FINAL CROP REPORT ==========")

    print("Image:", final_report["image"])

    print("Crop:", selected_crop)

    print(
        "Hybrid status:",
        diagnosis.get("hybrid_status")
    )

    print(
        "Needs review:",
        diagnosis.get("needs_review")
    )

    # --------------------------------------
    # G. DISPLAY MODEL PREDICTIONS
    # --------------------------------------

    print("\nMODEL PREDICTIONS")

    for prediction in predictions:

        print(

            prediction.get("source_model"),

            "->",

            prediction.get("disease"),

            "| Score:",

            prediction.get("model_score")
        )

    # --------------------------------------
    # H. DISPLAY CROP WEATHER CONTEXT
    # --------------------------------------

    print("\nCROP-LEVEL WEATHER CONTEXT")

    if weather_result["crop_weather_context"]:

        for alert in weather_result["crop_weather_context"]:

            print(
                "Alert:",
                alert["alert_level"]
            )

            print(
                "English:",
                alert["message_en"]
            )

            print(
                "Bangla:",
                alert["message_bn"]
            )

    else:

        print(
            "No weather assessment available for this crop."
        )

    # --------------------------------------
    # I. DISPLAY DISEASE-SPECIFIC MATCH
    # --------------------------------------

    print("\nDISEASE-SPECIFIC WEATHER MATCH")

    if weather_result["disease_specific_matches"]:

        for match in weather_result["disease_specific_matches"]:

            print(
                "Disease:",
                match["predicted_disease"]
            )

            print(
                "Predicted by:",
                match["predicted_by"]
            )

            print(
                "Weather alert:",
                match["weather_alert"]["alert_level"]
            )

    else:

        print(
            "No weather assessment specifically matched "
            "the predicted disease."
        )

    # --------------------------------------
    # J. FINAL OUTPUT
    # --------------------------------------

    print("\nFinal report saved:")

    print(report_file)

    print("\n======================================")

    return final_report


# ==========================================
# 6. TERMINAL EXECUTION
# ==========================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print(
            "Usage: python crop_guardian_engine.py "
            "image_path crop_name"
        )

        raise SystemExit(1)

    image_path = sys.argv[1]

    selected_crop = sys.argv[2]

    run_crop_guardian(
        image_path,
        selected_crop
    )
