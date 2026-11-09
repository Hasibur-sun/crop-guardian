
import csv
import json

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "weather_hourly.csv"

OUTPUT_FILE = (
    BASE_DIR / "eval" / "potato_late_blight_screen.json"
)

BANGLADESH_UTC_OFFSET = 6

MIN_TEMP_THRESHOLD = 10.0

RH_THRESHOLD = 90.0

REQUIRED_RH_HOURS = 6


# ==========================================
# 2. LOAD HOURLY DATA
# ==========================================

def load_data():

    daily = defaultdict(list)

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            utc_time = datetime.strptime(
                row["datetime_utc"],
                "%Y%m%d%H"
            )

            local_time = (
                utc_time
                + timedelta(hours=BANGLADESH_UTC_OFFSET)
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

            daily[local_time.date()].append({

                "timestamp": local_time,

                "temperature": get_value("T2M_C"),

                "humidity": get_value("RH2M_percent"),

                "rainfall": get_value(
                    "PRECTOTCORR_mm_hour"
                )
            })

    return daily


# ==========================================
# 3. DAILY WEATHER ANALYSIS
# ==========================================

def analyze_daily(daily):

    results = []

    for date in sorted(daily):

        records = daily[date]

        records.sort(
            key=lambda x: x["timestamp"]
        )

        valid_temp = [
            x["temperature"]
            for x in records
            if x["temperature"] is not None
        ]

        valid_rh = [
            x["humidity"]
            for x in records
            if x["humidity"] is not None
        ]

        complete = (
            len(records) == 24
            and len(valid_temp) == 24
            and len(valid_rh) == 24
        )

        if not complete:

            results.append({

                "date": str(date),

                "complete": False,

                "reason": (
                    "Incomplete 24-hour weather observations"
                )

            })

            continue

        minimum_temperature = min(valid_temp)

        high_humidity_hours = sum(
            x >= RH_THRESHOLD
            for x in valid_rh
        )

        results.append({

            "date": str(date),

            "complete": True,

            "minimum_temperature": round(
                minimum_temperature, 2
            ),

            "hours_rh_above_90": high_humidity_hours,

            "temperature_condition": (
                minimum_temperature >= MIN_TEMP_THRESHOLD
            ),

            "humidity_condition": (
                high_humidity_hours >= REQUIRED_RH_HOURS
            ),

            "daily_conditions_met": (
                minimum_temperature >= MIN_TEMP_THRESHOLD
                and high_humidity_hours >= REQUIRED_RH_HOURS
            )
        })

    return results


# ==========================================
# 4. CHECK TWO CONSECUTIVE DAYS
# ==========================================

def check_hutton_criteria(daily_results):

    qualifying_pairs = []

    for i in range(len(daily_results) - 1):

        first = daily_results[i]

        second = daily_results[i + 1]

        if not first["complete"] or not second["complete"]:
            continue

        first_date = datetime.strptime(
            first["date"], "%Y-%m-%d"
        ).date()

        second_date = datetime.strptime(
            second["date"], "%Y-%m-%d"
        ).date()

        # Confirm actual consecutive calendar days

        if second_date - first_date != timedelta(days=1):
            continue

        if (
            first["daily_conditions_met"]
            and second["daily_conditions_met"]
        ):

            qualifying_pairs.append({

                "start_date": first["date"],

                "end_date": second["date"],

                "first_day_rh_hours": (
                    first["hours_rh_above_90"]
                ),

                "second_day_rh_hours": (
                    second["hours_rh_above_90"]
                ),

                "minimum_temperature_day_1": (
                    first["minimum_temperature"]
                ),

                "minimum_temperature_day_2": (
                    second["minimum_temperature"]
                )
            })

    return qualifying_pairs


# ==========================================
# 5. MAIN
# ==========================================

def main():

    print("\n========== POTATO LATE BLIGHT SCREEN ==========")

    daily = load_data()

    if not daily:

        raise RuntimeError(
            "No hourly weather data found."
        )

    daily_results = analyze_daily(daily)

    qualifying_pairs = check_hutton_criteria(
        daily_results
    )

    complete_days = [
        x for x in daily_results
        if x["complete"]
    ]

    result = {

        "crop": "potato",

        "disease": "Late blight",

        "location": {

            "latitude": 23.8103,

            "longitude": 90.4125,

            "timezone": "Asia/Dhaka"
        },

        "method": "Exploratory Hutton Criteria comparison",

        "thresholds": {

            "minimum_temperature_c": MIN_TEMP_THRESHOLD,

            "relative_humidity_percent": RH_THRESHOLD,

            "required_hours_per_day": REQUIRED_RH_HOURS,

            "consecutive_days_required": 2
        },

        "complete_days": len(complete_days),

        "daily_results": daily_results,

        "qualifying_pairs": qualifying_pairs,

        "benchmark_met": len(qualifying_pairs) > 0,

        "interpretation": (
            "Hutton benchmark conditions were met in "
            "at least one consecutive-day pair."
            if qualifying_pairs
            else
            "No complete consecutive-day pair met "
            "all Hutton benchmark conditions."
        ),

        "limitations": [
            "This criterion was developed for Great Britain.",
            "It is not locally validated for Bangladesh.",
            "Hourly temperature minimum is a proxy for daily minimum temperature.",
            "Relative humidity is not a direct leaf-wetness measurement.",
            "Weather conditions do not confirm pathogen presence."
        ]
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

    # --------------------------------------
    # DISPLAY DAILY RESULTS
    # --------------------------------------

    print("\nDAILY WEATHER CONDITIONS\n")

    for day in daily_results:

        print("Date:", day["date"])

        if not day["complete"]:

            print("Incomplete day - excluded")

            print("-" * 40)

            continue

        print(
            "Minimum temperature:",
            day["minimum_temperature"]
        )

        print(
            "Hours RH >= 90%:",
            day["hours_rh_above_90"]
        )

        print(
            "Daily conditions met:",
            day["daily_conditions_met"]
        )

        print("-" * 40)

    # --------------------------------------
    # DISPLAY FINAL RESULT
    # --------------------------------------

    print("\nHUTTON BENCHMARK RESULT")

    print(
        "Complete days:",
        len(complete_days)
    )

    print(
        "Qualifying consecutive-day pairs:",
        len(qualifying_pairs)
    )

    print(
        "Benchmark met:",
        result["benchmark_met"]
    )

    print(
        "Interpretation:",
        result["interpretation"]
    )

    print("\nReport saved:")

    print(OUTPUT_FILE)

    print("\n================================================")


if __name__ == "__main__":

    main()
