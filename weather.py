
import csv
import requests
import argparse

from pathlib import Path
from datetime import datetime, timedelta, timezone


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "data"

OUTPUT_FILE = OUTPUT_DIR / "weather_daily.csv"

NASA_POWER_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)

DEFAULT_LATITUDE = 23.8103
DEFAULT_LONGITUDE = 90.4125

PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "PRECTOTCORR"
]

CSV_COLUMNS = [
    "date",
    "T2M_C",
    "T2M_MAX_C",
    "T2M_MIN_C",
    "RH2M_percent",
    "PRECTOTCORR_mm_day"
]


# ==========================================
# 2. DEFAULT DATE RANGE
# ==========================================

def get_default_dates():

    # Leave a 7-day buffer because NASA's
    # daily data may have reporting latency.

    end_date = (
        datetime.now(timezone.utc).date()
        - timedelta(days=7)
    )

    start_date = end_date - timedelta(days=13)

    return (
        start_date.strftime("%Y%m%d"),
        end_date.strftime("%Y%m%d")
    )


# ==========================================
# 3. FETCH NASA POWER DATA
# ==========================================

def fetch_weather(
    latitude,
    longitude,
    start_date,
    end_date
):

    print("\nConnecting to NASA POWER API...")

    params = {

        "parameters": ",".join(PARAMETERS),

        "community": "AG",

        "longitude": longitude,

        "latitude": latitude,

        "start": start_date,

        "end": end_date,

        "format": "JSON",

        "time-standard": "UTC"
    }

    try:

        response = requests.get(
            NASA_POWER_URL,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        payload = response.json()

    except requests.RequestException as e:

        raise RuntimeError(
            f"NASA POWER request failed: {e}"
        )

    except ValueError:

        raise RuntimeError(
            "NASA POWER returned invalid JSON."
        )

    # --------------------------------------
    # Extract response data
    # --------------------------------------

    try:

        weather_data = (
            payload["properties"]["parameter"]
        )

    except (KeyError, TypeError):

        raise RuntimeError(
            "Unexpected NASA POWER response structure."
        )

    if not weather_data:

        raise RuntimeError(
            "NASA POWER returned no weather data."
        )

    print("NASA POWER connection successful.")

    return weather_data


# ==========================================
# 4. PROCESS WEATHER DATA
# ==========================================

def process_weather(weather_data):

    print("\nProcessing weather records...")

    available_dates = sorted(
        set().union(
            *[
                set(weather_data.get(parameter, {}).keys())
                for parameter in PARAMETERS
            ]
        )
    )

    records = []

    for date in available_dates:

        record = {"date": date}

        for parameter in PARAMETERS:

            value = weather_data.get(
                parameter, {}
            ).get(date)

            # NASA uses -999 for missing values
            if value is None or float(value) == -999:

                record[parameter] = None

            else:

                record[parameter] = float(value)

        # Keep a record even if some parameters
        # are missing. Do not invent values.

        records.append(record)

    return records


# ==========================================
# 5. SAVE WEATHER CSV
# ==========================================

def save_weather(records):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=CSV_COLUMNS
        )

        writer.writeheader()

        for record in records:

            writer.writerow({

                "date": record["date"],

                "T2M_C": record["T2M"],

                "T2M_MAX_C": record["T2M_MAX"],

                "T2M_MIN_C": record["T2M_MIN"],

                "RH2M_percent": record["RH2M"],

                "PRECTOTCORR_mm_day": (
                    record["PRECTOTCORR"]
                )
            })

    print("\nWeather data saved successfully.")

    print("File:", OUTPUT_FILE)


# ==========================================
# 6. DISPLAY WEATHER SUMMARY
# ==========================================

def display_summary(
    records,
    latitude,
    longitude
):

    print("\n========== NASA POWER WEATHER ==========")

    print("Latitude:", latitude)

    print("Longitude:", longitude)

    print("Total records:", len(records))

    if records:

        print(
            "First date:",
            records[0]["date"]
        )

        print(
            "Last date:",
            records[-1]["date"]
        )

    print("\nRecent weather observations:\n")

    for record in records[-5:]:

        print("Date:", record["date"])

        print("Average temperature:", record["T2M"])

        print("Maximum temperature:", record["T2M_MAX"])

        print("Minimum temperature:", record["T2M_MIN"])

        print("Relative humidity:", record["RH2M"])

        print("Rainfall:", record["PRECTOTCORR"])

        print("-" * 40)

    print("\nSource: NASA POWER Daily API")

    print("Note: These are gridded weather estimates,")
    print("not direct measurements from the farm.")

    print("========================================")


# ==========================================
# 7. MAIN
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description="Crop Guardian NASA POWER weather collector"
    )

    parser.add_argument(
        "--latitude",
        type=float,
        default=DEFAULT_LATITUDE
    )

    parser.add_argument(
        "--longitude",
        type=float,
        default=DEFAULT_LONGITUDE
    )

    parser.add_argument(
        "--start",
        type=str,
        default=None
    )

    parser.add_argument(
        "--end",
        type=str,
        default=None
    )

    args = parser.parse_args()

    if not -90 <= args.latitude <= 90:
        raise ValueError("Invalid latitude.")

    if not -180 <= args.longitude <= 180:
        raise ValueError("Invalid longitude.")

    default_start, default_end = get_default_dates()

    start_date = args.start or default_start

    end_date = args.end or default_end

    # Validate dates
    start = datetime.strptime(
        start_date, "%Y%m%d"
    ).date()

    end = datetime.strptime(
        end_date, "%Y%m%d"
    ).date()

    if start > end:
        raise ValueError(
            "Start date cannot be after end date."
        )

    if end > datetime.now(timezone.utc).date():
        raise ValueError(
            "End date cannot be in the future."
        )

    print("\n========== CROP GUARDIAN ==========")

    print("NASA POWER WEATHER COLLECTION")

    print("===================================")

    print("Location:", args.latitude, args.longitude)

    print("Start date:", start_date)

    print("End date:", end_date)

    weather_data = fetch_weather(
        args.latitude,
        args.longitude,
        start_date,
        end_date
    )

    records = process_weather(
        weather_data
    )

    if not records:
        raise RuntimeError(
            "No daily weather records were returned."
        )

    save_weather(records)

    display_summary(
        records,
        args.latitude,
        args.longitude
    )


if __name__ == "__main__":

    main()
