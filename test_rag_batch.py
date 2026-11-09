
import json
import csv

from pathlib import Path
from rag import search


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_FILE = (
    BASE_DIR / "knowledge" / "disease_knowledge.json"
)

REPORT_FILE = BASE_DIR / "eval" / "rag_batch_results.csv"


# ==========================================
# 2. LOAD KNOWLEDGE BASE
# ==========================================

print("\nLoading knowledge base...")

with open(
    KNOWLEDGE_FILE,
    "r",
    encoding="utf-8"
) as f:

    entries = json.load(f)

print("Total entries:", len(entries))


# ==========================================
# 3. INITIALIZE TEST COUNTERS
# ==========================================

passed = 0
failed = 0

results = []


# ==========================================
# 4. TEST EVERY KNOWLEDGE ENTRY
# ==========================================

print("\n========== RAG BATCH TEST ==========\n")

for number, entry in enumerate(entries, start=1):

    crop = entry["crop"]
    disease = entry["disease"]
    expected_id = entry["id"]

    try:

        result = search(
            crop=crop,
            disease=disease
        )

        # Check retrieval status
        status_ok = result["status"] == "success"

        # Check whether expected ID was retrieved
        retrieved_ids = [
            item["id"]
            for item in result.get("matches", [])
        ]

        id_ok = expected_id in retrieved_ids

        # Check crop filtering
        crop_ok = all(
            item["id"] == expected_id
            or item.get("crop", crop) == crop
            for item in result.get("matches", [])
        )

        success = status_ok and id_ok and crop_ok

        if success:
            passed += 1
            test_status = "PASS"
        else:
            failed += 1
            test_status = "FAIL"

        error_message = ""

    except Exception as e:

        failed += 1
        test_status = "ERROR"
        error_message = str(e)

        retrieved_ids = []

    # Display individual result
    print(
        f"[{number:02d}/{len(entries)}] "
        f"{test_status}: {crop} - {disease}"
    )

    if test_status != "PASS":
        print("    Expected ID:", expected_id)
        print("    Retrieved IDs:", retrieved_ids)
        if error_message:
            print("    Error:", error_message)

    # Store result
    results.append({
        "crop": crop,
        "disease": disease,
        "expected_id": expected_id,
        "retrieved_ids": ", ".join(retrieved_ids),
        "status": test_status,
        "error": error_message
    })


# ==========================================
# 5. SAVE CSV REPORT
# ==========================================

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    REPORT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "crop",
            "disease",
            "expected_id",
            "retrieved_ids",
            "status",
            "error"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


# ==========================================
# 6. FINAL SUMMARY
# ==========================================

total = len(entries)

accuracy = (
    passed / total * 100
    if total else 0
)

print("\n========== FINAL SUMMARY ==========")

print("Total tests:", total)
print("Passed:", passed)
print("Failed:", failed)

print(f"Retrieval success rate: {accuracy:.2f}%")

print("\nCSV report saved:")
print(REPORT_FILE)

print("===================================")
