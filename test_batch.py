import csv, time
from pathlib import Path
from diagnosis import diagnose

rows, valid = [], 0
images = sorted(p for p in Path("test_images").iterdir()
                if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})

for p in images:
    try:
        r = diagnose(str(p))
        top = r["top3"][0] if r["top3"] else {"disease": "-", "confidence": 0}
        rows.append([p.name, "OK", r["is_plant_photo"], r["crop"],
                     top["disease"], round(top["confidence"], 2), r["photo_quality"]])
        valid += 1
    except Exception as e:
        rows.append([p.name, f"FAIL: {e}", "", "", "", "", ""])
    time.sleep(5)  # stay inside free-tier per-minute limits

Path("eval").mkdir(exist_ok=True)
with open("eval/day1_results.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["file", "status", "is_plant", "crop", "top1", "conf", "quality"])
    w.writerows(rows)

print(f"Valid JSON: {valid}/{len(images)}")