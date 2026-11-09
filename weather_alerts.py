
import json

from pathlib import Path
from datetime import datetime, timezone


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR / "eval" / "bangladesh_weather_risk.json"
)

OUTPUT_FILE = (
    BASE_DIR / "eval" / "weather_alerts.json"
)


# ==========================================
# 2. ALERT DEFINITIONS
# ==========================================

def generate_alert(model):

    crop = model["crop"]

    disease = model["disease"]

    assessment = model["assessment"]

    # --------------------------------------
    # POTATO LATE BLIGHT
    # --------------------------------------

    if crop == "potato":

        if assessment == "insufficient_data":

            level = "DATA_UNAVAILABLE"

            message = (
                "Insufficient weather data for "
                "potato late blight screening."
            )

            bangla = (
                "আলুর লেট ব্লাইট ঝুঁকি যাচাইয়ের জন্য "
                "পর্যাপ্ত আবহাওয়ার তথ্য পাওয়া যায়নি।"
            )

        elif assessment == "favorable_indicators_observed":

            level = "MONITOR"

            message = (
                "Some weather indicators favorable "
                "to late blight were observed. "
                "Inspect potato leaves regularly."
            )

            bangla = (
                "লেট ব্লাইটের অনুকূল কিছু আবহাওয়াগত "
                "সংকেত পাওয়া গেছে। আলুর পাতা নিয়মিত "
                "পর্যবেক্ষণ করুন।"
            )

        else:

            level = "NO_STRONG_SIGNAL"

            message = (
                "The selected late blight weather "
                "indicators were limited during the "
                "observation period. Continue monitoring."
            )

            bangla = (
                "পর্যবেক্ষণের সময়ে লেট ব্লাইটের "
                "নির্বাচিত আবহাওয়াগত সংকেত সীমিত ছিল। "
                "ফসল নিয়মিত পর্যবেক্ষণ করুন।"
            )

    # --------------------------------------
    # TOMATO EARLY BLIGHT
    # --------------------------------------

    elif crop == "tomato":

        if assessment == "insufficient_data":

            level = "DATA_UNAVAILABLE"

            message = (
                "Insufficient weather data for "
                "tomato early blight screening."
            )

            bangla = (
                "টমেটোর আর্লি ব্লাইট পর্যবেক্ষণের জন্য "
                "পর্যাপ্ত আবহাওয়ার তথ্য পাওয়া যায়নি।"
            )

        elif assessment == "incomplete_weather_data":

            level = "DATA_INCOMPLETE"

            message = (
                "Some required weather observations "
                "are missing. Screening is incomplete."
            )

            bangla = (
                "কিছু প্রয়োজনীয় আবহাওয়ার তথ্য অনুপস্থিত। "
                "পর্যবেক্ষণ সম্পূর্ণ হয়নি।"
            )

        else:

            level = "WEATHER_CONTEXT"

            message = (
                "Weather observations are available. "
                "No locally validated numerical early "
                "blight risk score is currently applied."
            )

            bangla = (
                "আবহাওয়ার তথ্য পাওয়া গেছে। তবে টমেটোর "
                "আর্লি ব্লাইটের জন্য স্থানীয়ভাবে যাচাইকৃত "
                "সংখ্যাগত ঝুঁকি মডেল এখনো প্রয়োগ করা হয়নি।"
            )

    # --------------------------------------
    # RICE BLAST
    # --------------------------------------

    elif crop == "rice":

        if assessment == "insufficient_data":

            level = "DATA_UNAVAILABLE"

            message = (
                "Insufficient 14-day weather data "
                "for rice blast screening."
            )

            bangla = (
                "ধানের ব্লাস্ট রোগ পর্যবেক্ষণের জন্য "
                "পর্যাপ্ত ১৪ দিনের আবহাওয়ার তথ্য নেই।"
            )

        elif assessment == "missing_weather_data":

            level = "DATA_INCOMPLETE"

            message = (
                "Required weather observations "
                "are missing."
            )

            bangla = (
                "প্রয়োজনীয় আবহাওয়ার কিছু তথ্য অনুপস্থিত।"
            )

        elif assessment == "non_consecutive_data":

            level = "DATA_INCOMPLETE"

            message = (
                "The 14-day weather observations "
                "are not consecutive."
            )

            bangla = (
                "১৪ দিনের আবহাওয়ার তথ্য ধারাবাহিক নয়।"
            )

        elif assessment == "research_conditions_met":

            level = "MONITOR"

            message = (
                "All three BRRI research weather "
                "conditions were met. Inspect rice "
                "fields and monitor for blast symptoms."
            )

            bangla = (
                "ব্রি-এর গবেষণায় উল্লেখিত তিনটি "
                "আবহাওয়াগত শর্ত পূরণ হয়েছে। "
                "ধানক্ষেত পর্যবেক্ষণ করুন এবং "
                "ব্লাস্ট রোগের লক্ষণ খেয়াল করুন।"
            )

        else:

            level = "RESEARCH_CONDITIONS_NOT_MET"

            message = (
                "The selected BRRI research weather "
                "conditions were not fully met. "
                "Continue routine field monitoring."
            )

            bangla = (
                "ব্রি-এর গবেষণায় উল্লেখিত নির্বাচিত "
                "আবহাওয়াগত শর্তগুলো সম্পূর্ণ পূরণ হয়নি। "
                "নিয়মিত ধানক্ষেত পর্যবেক্ষণ করুন।"
            )

    else:

        level = "UNSUPPORTED_CROP"

        message = (
            "No weather alert rule is available "
            "for this crop."
        )

        bangla = (
            "এই ফসলের জন্য আবহাওয়াভিত্তিক "
            "সতর্কতা নিয়ম এখনো তৈরি করা হয়নি।"
        )

    # --------------------------------------
    # FINAL ALERT
    # --------------------------------------

    return {

        "crop": crop,

        "disease": disease,

        "assessment": assessment,

        "alert_level": level,

        "message_en": message,

        "message_bn": bangla,

        "requires_field_inspection": (
            level == "MONITOR"
        ),

        "treatment_recommendation": None,

        "source": model.get("source"),

        "source_url": model.get("source_url"),

        "generated_at_utc": (
            datetime.now(timezone.utc).isoformat()
        ),

        "disclaimer": (
            "Weather indicators do not confirm "
            "the presence of disease."
        )
    }


# ==========================================
# 3. MAIN ALERT ENGINE
# ==========================================

def main():

    print("\n========== CROP GUARDIAN ALERT ENGINE ==========")

    # Load screening results

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Run bangladesh_weather_risk.py first."
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        weather_data = json.load(f)

    models = weather_data["screening_results"]

    alerts = []

    # Generate alerts for every crop

    for model in models:

        alert = generate_alert(model)

        alerts.append(alert)

        print("\nCrop:", alert["crop"])

        print("Disease:", alert["disease"])

        print("Alert:", alert["alert_level"])

        print("English:", alert["message_en"])

        print("Bangla:", alert["message_bn"])

        print("-" * 50)

    # Save alerts

    result = {

        "project": "Crop Guardian",

        "system": "Weather Alert Engine",

        "location": weather_data["location"],

        "data_source": weather_data["data_source"],

        "total_alerts": len(alerts),

        "alerts": alerts,

        "disclaimer": (
            "These are weather-based screening alerts, "
            "not confirmed disease diagnoses."
        )
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nAll alerts generated successfully.")

    print("Total alerts:", len(alerts))

    print("Saved:", OUTPUT_FILE)

    print("\n================================================")


if __name__ == "__main__":

    main()
