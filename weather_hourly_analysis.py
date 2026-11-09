
import csv
import json

from pathlib import Path
from datetime import datetime, timedelta
from statistics import mean


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "weather_hourly.csv"

OUTPUT_FILE = (
    BASE_DIR / "eval" / "hourly_analysis.json"
)


# ==========================================
# 2. LOAD HOURLY DATA
# ==========================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Run weather_hourly.py first."
        )

    records = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            timestamp = datetime.strptime(
                row["datetime_utc"],
                "%Y%m%d%H"
            )

            def get_value(key):

                value = row.get(key, "").strip()

                if not value:
                    return None

                try:

                    number = float(value)

                    return (
                        None if number == -999
                        else number
                    )

                except ValueError:

                    return None

            records.append({

                "timestamp": timestamp,

                "temperature": get_value("T2M_C"),

                "humidity": get_value("RH2M_percent"),

                "rainfall": get_value(
                    "PRECTOTCORR_mm_hour"
                )
            })

    records.sort(
        key=lambda x: x["timestamp"]
    )

    return records


# ==========================================
# 3. CONSECUTIVE HOUR ANALYSIS
# ==========================================

def analyze_humidity(records, threshold):

    longest_streak = 0

    current_streak = 0

    current_start = None

    longest_start = None
    longest_end = None

    qualifying_hours = []

    previous_timestamp = None

    for record in records:

        timestamp = record["timestamp"]

        humidity = record["humidity"]

        # Missing humidity or a time gap
        # breaks a consecutive-hour streak.

        if (
            humidity is None
            or (
                previous_timestamp is not None
                and timestamp - previous_timestamp
                != timedelta(hours=1)
            )
        ):

            current_streak = 0
            current_start = None

        if humidity is not None and humidity >= threshold:

            qualifying_hours.append(record)

            if current_streak == 0:

                current_start = timestamp

            current_streak += 1

            if current_streak > longest_streak:

                longest_streak = current_streak

                longest_start = current_start

                longest_end = timestamp

        else:

            current_streak = 0
            current_start = None

        previous_timestamp = timestamp

    return {

        "threshold_percent": threshold,

        "total_qualifying_hours": len(
            qualifying_hours
        ),

        "longest_consecutive_hours": longest_streak,

        "longest_period_start_utc": (
            longest_start.isoformat()
            if longest_start else None
        ),

        "longest_period_end_utc": (
            longest_end.isoformat()
            if longest_end else None
        ),

        "average_temperature_during_period": (

            round(
                mean([
                    x["temperature"]
                    for x in qualifying_hours
                    if x["temperature"] is not None
                ]),
                2
            )

            if any(
                x["temperature"] is not None
                for x in qualifying_hours
            )

            else None
        ),

        "rainfall_during_qualifying_hours_mm": round(
            sum(
                x["rainfall"]
                for x in qualifying_hours
                if x["rainfall"] is not None
            ),
            3
        ),

        "rainfall_observations": sum(
            x["rainfall"] is not None
            for x in qualifying_hours
        )
    }


# ==========================================
# 4. DATA COVERAGE
# ==========================================

def calculate_coverage(records):

    if not records:

        return {}

    expected_hours = (
        int(
            (
                records[-1]["timestamp"]
                - records[0]["timestamp"]
            ).total_seconds() / 3600
        ) + 1
    )

    valid_humidity = sum(
        x["humidity"] is not None
        for x in records
    )

    valid_temperature = sum(
        x["temperature"] is not None
        for x in records
    )

    valid_rainfall = sum(
        x["rainfall"] is not None
        for x in records
    )

    return {

        "records_received": len(records),

        "expected_hourly_records": expected_hours,

        "valid_temperature": valid_temperature,

        "valid_humidity": valid_humidity,

        "valid_rainfall": valid_rainfall,

        "missing_records": (
            expected_hours - len(records)
        )
    }


# ==========================================
# 5. MAIN ANALYSIS
# ==========================================

def main():

    print("\n========== HOURLY ANALYSIS ==========")

    records = load_data()

    if not records:

        raise RuntimeError(
            "No hourly weather records found."
        )

    # Calculate humidity thresholds

    humidity_90 = analyze_humidity(
        records,
        90
    )

    humidity_85 = analyze_humidity(
        records,
        85
    )

    coverage = calculate_coverage(
        records
    )

    # Calculate total rainfall

    rainfall_values = [
        x["rainfall"]
        for x in records
        if x["rainfall"] is not None
    ]

    total_rainfall = (
        round(sum(rainfall_values), 3)
        if rainfall_values else None
    )

    result = {

        "data_source": "NASA POWER Hourly API",

        "time_standard": "UTC",

        "start": records[0]["timestamp"].isoformat(),

        "end": records[-1]["timestamp"].isoformat(),

        "coverage": coverage,

        "total_rainfall_mm": total_rainfall,

        "humidity_analysis": {

            "above_90_percent": humidity_90,

            "above_85_percent": humidity_85
        },

        "note": (
            "Humidity is an environmental proxy, "
            "not a direct leaf-wetness measurement. "
            "This analysis does not confirm disease infection."
        )
    }

    # Save JSON report

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

    # --------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------

    print("\nDATA COVERAGE")

    print(
        "Records received:",
        coverage["records_received"]
    )

    print(
        "Expected records:",
        coverage["expected_hourly_records"]
    )

    print(
        "Missing records:",
        coverage["missing_records"]
    )

    print("\nTOTAL RAINFALL")

    print(
        "Total rainfall:",
        total_rainfall,
        "mm"
    )

    for key, analysis in [

        ("RH >= 90%", humidity_90),

        ("RH >= 85%", humidity_85)

    ]:

        print("\n", key)

        print(
            "Qualifying hours:",
            analysis["total_qualifying_hours"]
        )

        print(
            "Longest consecutive period:",
            analysis["longest_consecutive_hours"],
            "hours"
        )

        print(
            "Period start:",
            analysis["longest_period_start_utc"]
        )

        print(
            "Period end:",
            analysis["longest_period_end_utc"]
        )

        print(
            "Average temperature:",
            analysis["average_temperature_during_period"]
        )

        print(
            "Rainfall during qualifying hours:",
            analysis["rainfall_during_qualifying_hours_mm"],
            "mm"
        )

    print("\nReport saved:")

    print(OUTPUT_FILE)

    print("\n=====================================")


if __name__ == "__main__":

    main()
