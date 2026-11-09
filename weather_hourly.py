
import csv
import requests

from pathlib import Path
from datetime import datetime, timedelta, timezone


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "data"

OUTPUT_FILE = OUTPUT_DIR / "weather_hourly.csv"

API_URL = (
    "https://power.larc.nasa.gov/api/temporal/hourly/point"
)

LATITUDE = 23.8103
LONGITUDE = 90.4125

# NASA POWER Hourly API parameters
PARAMETERS = [
    "T2M",
    "RH2M",
     "PRECTOTCORR"
]

# Use SB for this combined hourly request.
COMMUNITY = "SB"

TIME_STANDARD = "UTC"

TIMEOUT = 90


# ==========================================
# 2. DATE RANGE
# ==========================================

def get_dates():

    # Two-day buffer for data availability.

    end = (
        datetime.now(timezone.utc).date()
        - timedelta(days=2)
    )

    start = end - timedelta(days=7)

    return (
        start.strftime("%Y%m%d"),
        end.strftime("%Y%m%d")
    )


# ==========================================
# 3. FETCH NASA POWER DATA
# ==========================================

def fetch_hourly():

    start, end = get_dates()

    params = {

        "parameters": ",".join(PARAMETERS),

        "community": COMMUNITY,

        "longitude": LONGITUDE,

        "latitude": LATITUDE,

        "start": start,

        "end": end,

        "format": "JSON",

        "time-standard": TIME_STANDARD
    }

    print("\n========== NASA POWER HOURLY ==========")

    print("Connecting to NASA POWER API...")

    print("Community:", COMMUNITY)

    print("Location:", LATITUDE, LONGITUDE)

    print("Parameters:", PARAMETERS)

    print("Start:", start)

    print("End:", end)

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=TIMEOUT
        )

        if response.status_code != 200:

            print(
                "\nNASA API Error:",
                response.status_code
            )

            print(
                "Details:",
                response.text[:2000]
            )

            raise RuntimeError(
                "NASA POWER request failed."
            )

        payload = response.json()

    except requests.RequestException as e:

        raise RuntimeError(
            f"NASA connection error: {e}"
        )

    except ValueError as e:

        raise RuntimeError(
            f"Invalid NASA JSON response: {e}"
        )

    # --------------------------------------
    # Extract weather parameters
    # --------------------------------------

    try:

        weather = (
            payload["properties"]["parameter"]
        )

    except (KeyError, TypeError):

        raise RuntimeError(
            "Unexpected NASA POWER response structure."
        )

    print("\nAvailable parameters:")

    print(list(weather.keys()))

    # --------------------------------------
    # Validate requested parameters
    # --------------------------------------

    missing = [
        parameter
        for parameter in PARAMETERS
        if parameter not in weather
    ]

    if missing:

        raise RuntimeError(
            f"Missing NASA parameters: {missing}. "
            f"Available: {list(weather.keys())}"
        )

    print("\nNASA POWER data retrieved successfully.")

    return weather, start, end


# ==========================================
# 4. PROCESS HOURLY DATA
# ==========================================

def process_hourly(weather):

    timestamps = sorted(
        set().union(
            *[
                set(weather[parameter].keys())
                for parameter in PARAMETERS
            ]
        )
    )

    records = []

    for timestamp in timestamps:

        record = {

            "datetime_utc": timestamp
        }

        for parameter in PARAMETERS:

            value = weather[parameter].get(
                timestamp
            )

            if value is None:

                record[parameter] = None

            else:

                value = float(value)

                # NASA missing-data indicator
                record[parameter] = (
                    None if value == -999 else value
                )

        records.append(record)

    return records


# ==========================================
# 5. SAVE HOURLY CSV
# ==========================================

def save_hourly(records):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    columns = [

        "datetime_utc",

        "T2M_C",

        "RH2M_percent",

        "PRECTOTCORR_mm_hour"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=columns
        )

        writer.writeheader()

        for record in records:

            writer.writerow({

                "datetime_utc": record["datetime_utc"],

                "T2M_C": record["T2M"],

                "RH2M_percent": record["RH2M"],

                "PRECTOTCORR_mm_hour": record["PRECTOTCORR"]
            })

    print("\nHourly CSV saved successfully.")

    print("File:", OUTPUT_FILE)


# ==========================================
# 6. DISPLAY WEATHER SUMMARY
# ==========================================

def display_summary(records, start, end):

    valid_temperature = [

        x["T2M"]
        for x in records
        if x["T2M"] is not None
    ]

    valid_humidity = [

        x["RH2M"]
        for x in records
        if x["RH2M"] is not None
    ]

    valid_rainfall = [

        x["PRECTOTCORR"]
        for x in records
        if x["PRECTOTCORR"] is not None
    ]

    high_humidity_hours = sum(

        x["RH2M"] >= 90
        for x in records
        if x["RH2M"] is not None
    )

    print("\n========== HOURLY WEATHER SUMMARY ==========")

    print("Location:", LATITUDE, LONGITUDE)

    print("Community:", COMMUNITY)

    print("Start:", start)

    print("End:", end)

    print("Total hourly records:", len(records))

    print(
        "Valid temperature observations:",
        len(valid_temperature)
    )

    print(
        "Valid humidity observations:",
        len(valid_humidity)
    )

    print(
        "Valid rainfall observations:",
        len(valid_rainfall)
    )

    print(
        "Hours with RH >= 90%:",
        high_humidity_hours
    )

    if valid_temperature:

        print(
            "Average temperature:",
            round(
                sum(valid_temperature)
                / len(valid_temperature),
                2
            )
        )

    if valid_humidity:

        print(
            "Average humidity:",
            round(
                sum(valid_humidity)
                / len(valid_humidity),
                2
            )
        )

    if valid_rainfall:

        print(
            "Total observed rainfall (mm):",
            round(
                sum(valid_rainfall),
                2
            )
        )

    else:

        print("Total observed rainfall: Unavailable")

    print("\nLatest 10 hourly observations:\n")

    for record in records[-10:]:

        print(

            record["datetime_utc"],

            "| Temperature:", record["T2M"],

            "| Humidity:", record["RH2M"],

            "| Rainfall:", record["PRECTOTCORR"]
        )

    print("\nSource: NASA POWER Hourly API")

    print(
        "Note: Gridded estimates are not direct "
        "farm or leaf-wetness measurements."
    )

    print("============================================")


# ==========================================
# 7. MAIN
# ==========================================

def main():

    weather, start, end = fetch_hourly()

    records = process_hourly(weather)

    if not records:

        raise RuntimeError(
            "No hourly observations returned."
        )

    save_hourly(records)

    display_summary(
        records,
        start,
        end
    )


if __name__ == "__main__":

    main()
