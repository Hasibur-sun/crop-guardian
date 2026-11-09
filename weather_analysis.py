
import csv
from pathlib import Path
from statistics import mean


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

WEATHER_FILE = (
    BASE_DIR / "data" / "weather_daily.csv"
)


# ==========================================
# 2. LOAD WEATHER DATA
# ==========================================

def load_weather():

    if not WEATHER_FILE.exists():

        raise FileNotFoundError(
            "Weather CSV not found. Run weather.py first."
        )

    records = []

    with open(
        WEATHER_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            def get_value(key):

                value = row.get(key, "").strip()

                if not value:
                    return None

                try:
                    return float(value)
                except ValueError:
                    return None

            records.append({

                "date": row["date"],

                "temperature": get_value("T2M_C"),

                "max_temperature": get_value("T2M_MAX_C"),

                "min_temperature": get_value("T2M_MIN_C"),

                "humidity": get_value("RH2M_percent"),

                "rainfall": get_value(
                    "PRECTOTCORR_mm_day"
                )
            })

    records.sort(
        key=lambda x: x["date"]
    )

    if not records:
        raise ValueError("No weather records found.")

    return records


# ==========================================
# 3. CALCULATE WINDOW STATISTICS
# ==========================================

def calculate_window(records, days):

    window = records[-days:]

    temperatures = [
        x["temperature"]
        for x in window
        if x["temperature"] is not None
    ]

    humidities = [
        x["humidity"]
        for x in window
        if x["humidity"] is not None
    ]

    rainfalls = [
        x["rainfall"]
        for x in window
        if x["rainfall"] is not None
    ]

    result = {

        "requested_days": days,

        "available_days": len(window),

        "temperature_days": len(temperatures),

        "humidity_days": len(humidities),

        "rainfall_days": len(rainfalls),

        "average_temperature": (
            mean(temperatures)
            if temperatures else None
        ),

        "average_humidity": (
            mean(humidities)
            if humidities else None
        ),

        "total_rainfall": (
            sum(rainfalls)
            if rainfalls else None
        ),

        "days_humidity_above_80": sum(
            x > 80 for x in humidities
        ),

        "days_humidity_above_90": sum(
            x > 90 for x in humidities
        ),

        "rainy_days": sum(
            x >= 1 for x in rainfalls
        )
    }

    return result


# ==========================================
# 4. DISPLAY RESULTS
# ==========================================

def display_window(result):

    print(
        f"\n========== LAST "
        f"{result['requested_days']} DAYS =========="
    )

    print(
        "Available days:",
        result["available_days"]
    )

    print(
        "Temperature observations:",
        result["temperature_days"]
    )

    print(
        "Humidity observations:",
        result["humidity_days"]
    )

    print(
        "Rainfall observations:",
        result["rainfall_days"]
    )

    print(
        "Average temperature:",
        result["average_temperature"]
    )

    print(
        "Average humidity:",
        result["average_humidity"]
    )

    print(
        "Total rainfall (mm):",
        result["total_rainfall"]
    )

    print(
        "Days RH > 80%:",
        result["days_humidity_above_80"]
    )

    print(
        "Days RH > 90%:",
        result["days_humidity_above_90"]
    )

    print(
        "Rainy days (>= 1 mm):",
        result["rainy_days"]
    )


# ==========================================
# 5. MAIN
# ==========================================

def main():

    print("\n========== WEATHER ANALYSIS ==========")

    records = load_weather()

    print(
        "Total weather records:",
        len(records)
    )

    print(
        "Date range:",
        records[0]["date"],
        "to",
        records[-1]["date"]
    )

    latest = records[-1]

    print("\nLATEST WEATHER OBSERVATION")

    print("Date:", latest["date"])

    print(
        "Temperature:",
        latest["temperature"]
    )

    print(
        "Humidity:",
        latest["humidity"]
    )

    print(
        "Rainfall:",
        latest["rainfall"]
    )

    # Calculate rolling windows

    for days in [3, 7]:

        result = calculate_window(
            records,
            days
        )

        display_window(result)

    print("\n======================================")

    print(
        "Note: These are weather indicators, "
        "not confirmed disease-risk predictions."
    )


if __name__ == "__main__":

    main()
