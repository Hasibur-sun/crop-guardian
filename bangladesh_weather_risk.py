
import csv
import json

from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

HOURLY_FILE = BASE_DIR / "data" / "weather_hourly.csv"

DAILY_FILE = BASE_DIR / "data" / "weather_daily.csv"

OUTPUT_FILE = (
    BASE_DIR / "eval" / "bangladesh_weather_risk.json"
)

LOCAL_OFFSET = timedelta(hours=6)

# Potato screening parameters
POTATO_TEMP_MIN = 16.0
POTATO_TEMP_MAX = 20.0

# Experimental humidity proxy.
# BAMIS does not specify a numerical RH threshold
# for potato late blight on its disease page.
POTATO_HUMIDITY_PROXY = 90.0

# Rice blast research parameters from BRRI
RICE_MIN_TEMP_THRESHOLD = 21.0
RICE_AVG_TEMP_THRESHOLD = 25.5
RICE_HUMIDITY_THRESHOLD = 85.0

RICE_WINDOW_DAYS = 14

TOMATO_WINDOW_DAYS = 7


# ==========================================
# 2. GENERAL CSV READER
# ==========================================

def read_csv(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return list(csv.DictReader(f))


def number(value):

    if value is None or str(value).strip() == "":

        return None

    try:

        value = float(value)

        if value == -999:

            return None

        return value

    except ValueError:

        return None


# ==========================================
# 3. LOAD HOURLY DATA
# ==========================================

def load_hourly():

    rows = read_csv(HOURLY_FILE)

    records = []

    for row in rows:

        utc_time = datetime.strptime(
            row["datetime_utc"],
            "%Y%m%d%H"
        )

        local_time = utc_time + LOCAL_OFFSET

        records.append({

            "timestamp": local_time,

            "temperature": number(
                row.get("T2M_C")
            ),

            "humidity": number(
                row.get("RH2M_percent")
            ),

            "rainfall": number(
                row.get("PRECTOTCORR_mm_hour")
            )
        })

    records.sort(
        key=lambda x: x["timestamp"]
    )

    return records


# ==========================================
# 4. LOAD DAILY DATA
# ==========================================

def load_daily():

    rows = read_csv(DAILY_FILE)

    records = []

    for row in rows:

        date = datetime.strptime(
            row["date"],
            "%Y%m%d"
        ).date()

        records.append({

            "date": date,

            "temperature": number(
                row.get("T2M_C")
            ),

            "max_temperature": number(
                row.get("T2M_MAX_C")
            ),

            "min_temperature": number(
                row.get("T2M_MIN_C")
            ),

            "humidity": number(
                row.get("RH2M_percent")
            ),

            "rainfall": number(
                row.get("PRECTOTCORR_mm_day")
            )
        })

    records.sort(
        key=lambda x: x["date"]
    )

    return records


# ==========================================
# 5. BUILD COMPLETE LOCAL DAYS
# ==========================================

def build_local_days(hourly_records):

    grouped = defaultdict(list)

    for record in hourly_records:

        grouped[
            record["timestamp"].date()
        ].append(record)

    daily_groups = []

    for date in sorted(grouped):

        observations = grouped[date]

        observations.sort(
            key=lambda x: x["timestamp"]
        )

        timestamps = [
            x["timestamp"]
            for x in observations
        ]

        complete = (

            len(observations) == 24

            and len(set(timestamps)) == 24

            and timestamps[0].hour == 0

            and timestamps[-1].hour == 23

            and all(
                x["temperature"] is not None
                and x["humidity"] is not None
                for x in observations
            )
        )

        if complete:

            daily_groups.append({

                "date": date,

                "observations": observations
            })

    return daily_groups


# ==========================================
# 6. POTATO LATE BLIGHT SCREENING
# ==========================================

def screen_potato(hourly_records):

    local_days = build_local_days(
        hourly_records
    )

    window = local_days[-7:]

    if len(window) < 7:

        return {

            "crop": "potato",

            "disease": "Late blight",

            "assessment": "insufficient_data",

            "complete_days": len(window),

            "required_days": 7
        }

    daily_results = []

    for day in window:

        observations = day["observations"]

        favorable_temp_hours = [

            x for x in observations

            if POTATO_TEMP_MIN
            <= x["temperature"]
            <= POTATO_TEMP_MAX
        ]

        high_humidity_hours = [

            x for x in observations

            if x["humidity"]
            >= POTATO_HUMIDITY_PROXY
        ]

        combined_hours = [

            x for x in observations

            if (
                POTATO_TEMP_MIN
                <= x["temperature"]
                <= POTATO_TEMP_MAX

                and x["humidity"]
                >= POTATO_HUMIDITY_PROXY
            )
        ]

        rainy_hours = [

            x for x in observations

            if x["rainfall"] is not None
            and x["rainfall"] > 0
        ]

        daily_results.append({

            "date": str(day["date"]),

            "minimum_temperature": round(
                min(
                    x["temperature"]
                    for x in observations
                ),
                2
            ),

            "hours_temperature_16_20": len(
                favorable_temp_hours
            ),

            "hours_humidity_above_90": len(
                high_humidity_hours
            ),

            "combined_temperature_humidity_hours": len(
                combined_hours
            ),

            "rainy_hours": len(rainy_hours),

            "rainfall_mm": round(
                sum(
                    x["rainfall"]
                    for x in observations
                    if x["rainfall"] is not None
                ),
                3
            )
        })

    total_combined = sum(
        x["combined_temperature_humidity_hours"]
        for x in daily_results
    )

    total_rainy = sum(
        x["rainy_hours"]
        for x in daily_results
    )

    if total_combined > 0:

        assessment = "favorable_indicators_observed"

    else:

        assessment = "limited_favorable_indicators"

    return {

        "crop": "potato",

        "disease": "Late blight",

        "assessment": assessment,

        "complete_days_analyzed": len(window),

        "observed_indicators": {

            "hours_temperature_16_20": sum(
                x["hours_temperature_16_20"]
                for x in daily_results
            ),

            "hours_humidity_above_90": sum(
                x["hours_humidity_above_90"]
                for x in daily_results
            ),

            "combined_temperature_humidity_hours": (
                total_combined
            ),

            "rainy_hours": total_rainy,

            "total_rainfall_mm": round(
                sum(
                    x["rainfall_mm"]
                    for x in daily_results
                ),
                3
            )
        },

        "daily_results": daily_results,

        "threshold_notes": {

            "temperature": (
                "16-20 C from BAMIS/DAE."
            ),

            "humidity": (
                "90% is an experimental project proxy, "
                "not a numerical BAMIS threshold."
            ),

            "rainfall": (
                "Observed rainfall is a moisture indicator, "
                "not a direct measurement of fog or leaf wetness."
            )
        },

        "source": (
            "Bangladesh Agro-Meteorological "
            "Information Service (BAMIS), DAE"
        ),

        "source_url": (
            "https://www.bamis.gov.bd/en/diseases/1/all/52/"
        )
    }


# ==========================================
# 7. TOMATO EARLY BLIGHT SCREENING
# ==========================================

def screen_tomato(daily_records):

    window = daily_records[-TOMATO_WINDOW_DAYS:]

    if len(window) < TOMATO_WINDOW_DAYS:

        return {

            "crop": "tomato",

            "disease": "Early blight",

            "assessment": "insufficient_data",

            "available_days": len(window)
        }

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

    complete = (

        len(temperatures) == TOMATO_WINDOW_DAYS

        and len(humidities) == TOMATO_WINDOW_DAYS

        and len(rainfalls) == TOMATO_WINDOW_DAYS
    )

    if not complete:

        return {

            "crop": "tomato",

            "disease": "Early blight",

            "assessment": "incomplete_weather_data"
        }

    return {

        "crop": "tomato",

        "disease": "Early blight",

        "assessment": "weather_context_only",

        "window_days": TOMATO_WINDOW_DAYS,

        "observed_indicators": {

            "average_temperature": round(
                mean(temperatures),
                2
            ),

            "average_humidity": round(
                mean(humidities),
                2
            ),

            "total_rainfall_mm": round(
                sum(rainfalls),
                2
            ),

            "maximum_humidity": max(humidities),

            "minimum_humidity": min(humidities)
        },

        "interpretation": (
            "Weather observations collected successfully. "
            "No locally validated numerical Early blight "
            "risk equation is applied."
        ),

        "source": (
            "BAMIS Bangladesh regional tomato "
            "Early blight disease-weather calendars"
        ),

        "source_url": (
            "https://www.bamis.gov.bd/calendar/3/13/132"
        )
    }


# ==========================================
# 8. RICE BLAST SCREENING
# ==========================================

def screen_rice(daily_records):

    window = daily_records[-RICE_WINDOW_DAYS:]

    if len(window) < RICE_WINDOW_DAYS:

        return {

            "crop": "rice",

            "disease": "Blast",

            "assessment": "insufficient_data",

            "available_days": len(window),

            "required_days": RICE_WINDOW_DAYS
        }

    # Check consecutive calendar dates

    consecutive = all(

        window[i]["date"]
        - window[i - 1]["date"]
        == timedelta(days=1)

        for i in range(1, len(window))
    )

    if not consecutive:

        return {

            "crop": "rice",

            "disease": "Blast",

            "assessment": "non_consecutive_data"
        }

    required_fields = [

        "temperature",

        "min_temperature",

        "humidity"
    ]

    for record in window:

        for field in required_fields:

            if record[field] is None:

                return {

                    "crop": "rice",

                    "disease": "Blast",

                    "assessment": "missing_weather_data"
                }

    avg_temperature = mean(
        x["temperature"]
        for x in window
    )

    avg_min_temperature = mean(
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

    condition_1 = (
        avg_min_temperature
        > RICE_MIN_TEMP_THRESHOLD
    )

    condition_2 = (
        avg_temperature
        > RICE_AVG_TEMP_THRESHOLD
    )

    # BRRI specifies humidity above 85%
    # for at least 14 consecutive days.

    condition_3 = all(

        h > RICE_HUMIDITY_THRESHOLD

        for h in humidity_values
    )

    conditions_met = sum([

        condition_1,

        condition_2,

        condition_3
    ])

    return {

        "crop": "rice",

        "disease": "Blast",

        "assessment": (
            "research_conditions_met"
            if conditions_met == 3
            else "research_conditions_not_met"
        ),

        "window_days": RICE_WINDOW_DAYS,

        "conditions_met": conditions_met,

        "total_conditions": 3,

        "observed_indicators": {

            "average_minimum_temperature": round(
                avg_min_temperature,
                2
            ),

            "average_daily_temperature": round(
                avg_temperature,
                2
            ),

            "average_daily_humidity": round(
                avg_humidity,
                2
            ),

            "days_humidity_above_85": sum(
                h > RICE_HUMIDITY_THRESHOLD
                for h in humidity_values
            )
        },

        "conditions": {

            "average_minimum_temperature_above_21": (
                condition_1
            ),

            "average_daily_temperature_above_25_5": (
                condition_2
            ),

            "humidity_above_85_for_14_days": (
                condition_3
            )
        },

        "source": (
            "Bangladesh Rice Research Institute "
            "Research Progress 2023-2024"
        ),

        "source_url": (
            "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/"
            "n/axvjbnqprylg/b/V2Ministry/o/office-brri/2024/12/"
            "9963aa922c5d40568819f396ae34074c.pdf"
        ),

        "note": (
            "These are BRRI research screening conditions, "
            "not a calibrated disease probability."
        )
    }


# ==========================================
# 9. RUN ALL SCREENING MODULES
# ==========================================

def main():

    print("\n========== BANGLADESH WEATHER ENGINE ==========")

    hourly_records = load_hourly()

    daily_records = load_daily()

    print(
        "Hourly observations:",
        len(hourly_records)
    )

    print(
        "Daily observations:",
        len(daily_records)
    )

    potato = screen_potato(
        hourly_records
    )

    tomato = screen_tomato(
        daily_records
    )

    rice = screen_rice(
        daily_records
    )

    result = {

        "project": "Crop Guardian",

        "engine": "Bangladesh Weather Screening v1",

        "location": {

            "latitude": 23.8103,

            "longitude": 90.4125,

            "timezone": "Asia/Dhaka"
        },

        "data_source": "NASA POWER",

        "screening_results": [

            potato,

            tomato,

            rice
        ],

        "limitations": [

            "Weather indicators do not confirm crop infection.",

            "NASA POWER data are gridded estimates.",

            "Potato humidity threshold is an experimental proxy.",

            "Tomato assessment is contextual, not a validated risk score.",

            "Rice criteria are based on BRRI research and require local validation.",

            "Crop growth stage and pathogen presence are not yet included."
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
    # DISPLAY RESULTS
    # --------------------------------------

    for model in result["screening_results"]:

        print("\nCrop:", model["crop"])

        print("Disease:", model["disease"])

        print(
            "Assessment:",
            model["assessment"]
        )

        print(
            "Observed indicators:",
            model.get(
                "observed_indicators",
                "Not available"
            )
        )

        print("-" * 50)

    print("\nResults saved:")

    print(OUTPUT_FILE)

    print("\n==============================================")


if __name__ == "__main__":

    main()
