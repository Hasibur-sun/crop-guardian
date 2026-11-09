
import csv
import json

from pathlib import Path
from statistics import mean


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

WEATHER_FILE = BASE_DIR / "data" / "weather_daily.csv"

OUTPUT_DIR = BASE_DIR / "eval"

OUTPUT_FILE = OUTPUT_DIR / "weather_risk_results.json"


# ==========================================
# 2. LOAD WEATHER DATA
# ==========================================

def load_weather():

    if not WEATHER_FILE.exists():

        raise FileNotFoundError(
            "Run weather.py before weather_risk.py"
        )

    records = []

    with open(
        WEATHER_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            def number(key):

                value = row.get(key, "").strip()

                if not value:
                    return None

                try:

                    result = float(value)

                    if result == -999:
                        return None

                    return result

                except ValueError:

                    return None

            records.append({

                "date": row["date"],

                "temperature": number("T2M_C"),

                "max_temperature": number("T2M_MAX_C"),

                "min_temperature": number("T2M_MIN_C"),

                "humidity": number("RH2M_percent"),

                "rainfall": number(
                    "PRECTOTCORR_mm_day"
                )
            })

    records.sort(
        key=lambda x: x["date"]
    )

    return records


# ==========================================
# 3. DATA VALIDATION
# ==========================================

def validate_window(records, days):

    if len(records) < days:

        return False

    window = records[-days:]

    required = [
        "temperature",
        "min_temperature",
        "humidity",
        "rainfall"
    ]

    for record in window:

        for field in required:

            if record[field] is None:

                return False

    return True


# ==========================================
# 4. POTATO LATE BLIGHT SCREENING
# ==========================================

def potato_late_blight(records):

    window = records[-7:]

    return {

        "crop": "potato",

        "disease": "Late blight",

        "assessment": "insufficient_temporal_resolution",

        "observed_indicators": {

            "days_available": len(window),

            "average_humidity": (
                round(mean([
                    x["humidity"]
                    for x in window
                    if x["humidity"] is not None
                ]), 2)
                if any(
                    x["humidity"] is not None
                    for x in window
                )
                else None
            ),

            "rainy_days": sum(
                x["rainfall"] >= 0.1
                for x in window
                if x["rainfall"] is not None
            )
        },

        "reason": (
            "A validated late blight infection assessment "
            "requires hourly temperature and sustained "
            "relative humidity or leaf wetness observations. "
            "Daily averages cannot establish infection periods."
        ),

        "source": "UC IPM late blight forecasting references"
    }


# ==========================================
# 5. TOMATO EARLY BLIGHT SCREENING
# ==========================================

def tomato_early_blight(records):

    window = records[-7:]

    favorable_days = []

    for record in window:

        temp = record["temperature"]

        humidity = record["humidity"]

        rainfall = record["rainfall"]

        if None in (temp, humidity, rainfall):

            continue

        # Warm temperature range used as a
        # broad environmental screening range.

        warm = 15 <= temp <= 30

        # Rainfall or high RH is used only as
        # a moisture proxy, not leaf wetness.

        moisture_indicator = (
            rainfall >= 0.1
            or humidity >= 90
        )

        if warm and moisture_indicator:

            favorable_days.append(
                record["date"]
            )

    return {

        "crop": "tomato",

        "disease": "Early blight",

        "assessment": "exploratory_weather_screen",

        "window_days": len(window),

        "favorable_indicator_days": len(
            favorable_days
        ),

        "dates_with_favorable_indicators": (
            favorable_days
        ),

        "interpretation": (
            "Warm conditions and moisture indicators "
            "were observed. This suggests potentially "
            "favorable environmental conditions, but "
            "does not confirm disease infection."
            if favorable_days
            else
            "The selected warm and moisture indicators "
            "were not observed together in the available "
            "daily records."
        ),

        "limitation": (
            "Daily rainfall and average humidity cannot "
            "determine actual leaf wetness duration."
        ),

        "source": (
            "University of Connecticut Extension "
            "and University of Minnesota Extension"
        )
    }


# ==========================================
# 6. RICE BLAST SCREENING
# ==========================================

def rice_blast(records):

    if not validate_window(records, 14):

        return {

            "crop": "rice",

            "disease": "Blast",

            "assessment": "insufficient_data",

            "reason": (
                "Complete 14-day temperature, humidity "
                "and minimum-temperature observations "
                "are required for this screening rule."
            )
        }

    window = records[-14:]

    avg_temperature = mean(
        x["temperature"]
        for x in window
    )

    avg_minimum_temperature = mean(
        x["min_temperature"]
        for x in window
    )

    humidity_values = [
        x["humidity"]
        for x in window
    ]

    avg_humidity = mean(
        humidity_values
    )

    # BRRI research screening conditions:
    # 1. Average minimum temperature > 21 C
    # 2. Average daily temperature > 25.5 C
    # 3. Daily average humidity > 85%
    #    for 14 consecutive days.

    condition_1 = (
        avg_minimum_temperature > 21
    )

    condition_2 = (
        avg_temperature > 25.5
    )

    condition_3 = all(
        h > 85
        for h in humidity_values
    )

    conditions_met = [
        condition_1,
        condition_2,
        condition_3
    ]

    met_count = sum(conditions_met)

    if met_count == 3:

        assessment = "research_conditions_met"

    else:

        assessment = "research_conditions_not_met"

    return {

        "crop": "rice",

        "disease": "Blast",

        "assessment": assessment,

        "research_conditions_met": met_count,

        "total_conditions": 3,

        "observed_indicators": {

            "average_temperature": round(
                avg_temperature, 2
            ),

            "average_minimum_temperature": round(
                avg_minimum_temperature, 2
            ),

            "average_humidity": round(
                avg_humidity, 2
            ),

            "consecutive_days_humidity_above_85": sum(
                h > 85
                for h in humidity_values
            )
        },

        "conditions": {

            "minimum_temperature_above_21": condition_1,

            "average_temperature_above_25_5": condition_2,

            "humidity_above_85_for_14_days": condition_3
        },

        "interpretation": (
            "All three BRRI research weather conditions "
            "were met. This is an environmental warning "
            "signal, not confirmation of rice blast."
            if met_count == 3
            else
            f"{met_count} of 3 BRRI research conditions "
            "were met. The full research screening "
            "condition was not satisfied."
        ),

        "source": (
            "Bangladesh Rice Research Institute "
            "Research Progress 2023-2024"
        )
    }


# ==========================================
# 7. RUN ALL SCREENING MODELS
# ==========================================

def run_screening():

    records = load_weather()

    if not records:

        raise RuntimeError(
            "No weather records available."
        )

    print("\n========== WEATHER RISK SCREENING ==========")

    print("Weather records:", len(records))

    print(
        "Date range:",
        records[0]["date"],
        "to",
        records[-1]["date"]
    )

    results = {

        "location": {

            "latitude": 23.8103,

            "longitude": 90.4125,

            "description": "Dhaka demonstration location"
        },

        "data_source": "NASA POWER",

        "models": [

            potato_late_blight(records),

            tomato_early_blight(records),

            rice_blast(records)
        ]
    }

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    for model in results["models"]:

        print("\nCrop:", model["crop"])

        print("Disease:", model["disease"])

        print("Assessment:", model["assessment"])

        print(
            "Interpretation:",
            model.get(
                "interpretation",
                model.get("reason", "")
            )
        )

        print("-" * 45)

    print("\nResults saved:", OUTPUT_FILE)

    print("\n============================================")


if __name__ == "__main__":

    run_screening()
