from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

BASE_DIR = Path(__file__).resolve().parent
EVAL_DIR = BASE_DIR / "eval"


def _safe(value: Any, fallback: str = "Not recorded") -> str:
    if value is None or str(value).strip() == "":
        return fallback
    return str(value).strip()


def _report_status(report: dict) -> str:
    diagnosis = report.get("diagnosis", {}) or {}
    return _safe(diagnosis.get("hybrid_status", diagnosis.get("status", "uncertain")))


def load_diagnosis_history(eval_dir: Path | str = EVAL_DIR) -> list[dict]:
    """Load saved per-image diagnosis reports; ignore malformed JSON files."""
    folder = Path(eval_dir)
    entries = []
    if not folder.exists():
        return entries

    for path in folder.glob("*_report.json"):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(report, dict) or "diagnosis" not in report:
                continue
            stat = path.stat()
            entries.append({
                "path": path,
                "report": report,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "crop": _safe(report.get("selected_crop"), "unknown").lower(),
                "image": _safe(report.get("image"), path.stem),
                "status": _report_status(report),
                "needs_review": bool((report.get("safety") or {}).get(
                    "human_review_required", (report.get("diagnosis") or {}).get("needs_review", True)
                )),
            })
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue

    return sorted(entries, key=lambda item: item["modified"], reverse=True)


def _register_pdf_font() -> str:
    """Register a Windows Unicode font when available; otherwise use Helvetica."""
    candidates = [
        Path(r"C:\Windows\Fonts\Nirmala.ttf"),
        Path(r"C:\Windows\Fonts\NirmalaUI.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for font_path in candidates:
        if font_path.exists():
            try:
                if "CropGuardianUnicode" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("CropGuardianUnicode", str(font_path)))
                return "CropGuardianUnicode"
            except Exception:
                pass
    return "Helvetica"


def build_diagnosis_pdf(report: dict, language: str = "English") -> bytes:
    """Build a plain-language farmer report; technical model metadata is omitted."""
    if not isinstance(report, dict):
        raise TypeError("A diagnosis report dictionary is required.")

    from xml.sax.saxutils import escape
    font_name = _register_pdf_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=19 * mm, leftMargin=19 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm,
        title="Crop Guardian – Plant Health Report", author="Crop Guardian",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="FarmerTitle", parent=styles["Title"], fontName=font_name,
        fontSize=21, leading=26, textColor=colors.HexColor("#0A3323"), alignment=TA_LEFT, spaceAfter=4*mm))
    styles.add(ParagraphStyle(name="FarmerHead", parent=styles["Heading2"], fontName=font_name,
        fontSize=12, leading=16, textColor=colors.HexColor("#105666"), spaceBefore=4*mm, spaceAfter=2*mm))
    styles.add(ParagraphStyle(name="FarmerBody", parent=styles["BodyText"], fontName=font_name,
        fontSize=9.5, leading=14, textColor=colors.HexColor("#183B2C"), spaceAfter=2.5*mm))
    styles.add(ParagraphStyle(name="FarmerSmall", parent=styles["BodyText"], fontName=font_name,
        fontSize=8, leading=11, textColor=colors.HexColor("#586B60")))

    diagnosis = report.get("diagnosis", {}) or {}
    weather = report.get("weather_intelligence", {}) or {}
    safety = report.get("safety", {}) or {}
    predictions = diagnosis.get("model_predictions", []) or []
    status = diagnosis.get("hybrid_status", diagnosis.get("status", "uncertain"))
    needs_review = bool(safety.get("human_review_required", diagnosis.get("needs_review", True)))
    guidance_allowed = bool(diagnosis.get("farmer_guidance_allowed", False)) and not needs_review
    crop = _safe(report.get("selected_crop"), "crop").replace("_", " ").title()
    is_bn = str(language).lower().startswith(("বাংলা", "bangla"))

    def nice(value):
        return _safe(value, "").replace("_", " ").strip().title()

    disease_names = [nice(p.get("disease")) for p in predictions
                     if p.get("disease") and str(p.get("disease")).lower() not in {"healthy", "unknown"}]
    same_disease = bool(disease_names) and len({x.lower() for x in disease_names}) == 1 and status == "model_agreement"
    healthy_only = bool(predictions) and all(str(p.get("disease", "")).lower() == "healthy" for p in predictions)

    if is_bn:
        title = "আপনার গাছের স্বাস্থ্য প্রতিবেদন"
        intro = "পাতার ছবির ভিত্তিতে প্রাথমিক সহায়তা। এটি নিশ্চিত রোগ নির্ণয় নয়।"
        problem_heading, cause_heading, action_heading = "সম্ভাব্য সমস্যা", "এটি কেন হতে পারে", "এখন কী করবেন"
        treatment_heading, weather_heading, note_heading = "চিকিৎসা ও ওষুধ", "আপনার এলাকার আবহাওয়া", "গুরুত্বপূর্ণ কথা"
        crop_line = f"ফসল: {crop}"
        review_line = "কৃষি কর্মকর্তার পরামর্শ নিন।" if needs_review else "গাছ পর্যবেক্ষণ চালিয়ে যান।"
        no_treatment = "এই ফলাফলের জন্য যাচাইকৃত ওষুধের নির্দেশনা নেই। কীটনাশক ব্যবহারের আগে স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।"
        generic_note = "ছবির ফলাফল নিশ্চিত নয়। সমস্যা বাড়লে কৃষি কর্মকর্তার পরামর্শ নিন।"
    else:
        title = "Your plant health report"
        intro = "Simple guidance based on your leaf photo. This is not a confirmed diagnosis."
        problem_heading, cause_heading, action_heading = "Possible problem", "Why this may be happening", "What to do now"
        treatment_heading, weather_heading, note_heading = "Treatment and medicine", "Weather in your area", "Important"
        crop_line = f"Crop: {crop}"
        review_line = "Please ask a local agricultural officer to check the plant." if needs_review else "Keep monitoring the plant for changes."
        no_treatment = "We do not have verified medicine instructions for this result. Ask a local agricultural officer before applying any pesticide or treatment."
        generic_note = "This photo-based result is not certain. Seek local agricultural advice if symptoms worsen."

    story = [Paragraph(escape(title), styles["FarmerTitle"]),
             Paragraph(escape(intro), styles["FarmerSmall"]), Spacer(1, 4*mm),
             Paragraph(escape(crop_line), styles["FarmerBody"])]

    if status == "crop_mismatch":
        problem = "The photo may not show the crop you selected. Please check the crop and take another clear photo." if not is_bn else "ছবির গাছটি নির্বাচিত ফসল নাও হতে পারে। ফসলের ধরন যাচাই করে আবার পরিষ্কার ছবি তুলুন।"
    elif healthy_only and not needs_review:
        problem = "No clear disease symptoms were identified in this photo." if not is_bn else "এই ছবিতে রোগের স্পষ্ট লক্ষণ পাওয়া যায়নি।"
    elif same_disease:
        problem = (f"The symptoms may be consistent with {disease_names[0]}." if not is_bn else f"পাতার লক্ষণ {disease_names[0]} রোগের সঙ্গে মিলতে পারে।")
    else:
        problem = "We could not identify the problem confidently from this photo." if not is_bn else "এই ছবি থেকে সমস্যাটি নিশ্চিতভাবে শনাক্ত করা যায়নি।"
    story += [Paragraph(escape(problem_heading), styles["FarmerHead"]), Paragraph(escape(problem), styles["FarmerBody"])]

    if same_disease:
        cause = ("A disease name alone cannot establish the cause on your farm. Check other leaves and consider recent rain, watering and field conditions." if not is_bn else
                 "শুধু রোগের নাম দেখে জমিতে রোগের সঠিক কারণ নিশ্চিত করা যায় না। অন্য পাতাও দেখুন এবং সাম্প্রতিক বৃষ্টি, সেচ ও জমির অবস্থা বিবেচনা করুন।")
        story += [Paragraph(escape(cause_heading), styles["FarmerHead"]), Paragraph(escape(cause), styles["FarmerBody"])]

    action = ("Take a clear photo of the whole plant and affected leaves. Check whether similar spots are spreading. Remove badly damaged leaves only when advised and dispose of diseased debris safely. Avoid wetting foliage where practical." if not is_bn else
              "গাছ ও আক্রান্ত পাতার পরিষ্কার ছবি তুলুন। একই ধরনের দাগ ছড়াচ্ছে কি না দেখুন। প্রয়োজন হলে কৃষি কর্মকর্তার পরামর্শে বেশি আক্রান্ত পাতা সরান।")
    story += [Paragraph(escape(action_heading), styles["FarmerHead"]), Paragraph(escape(action), styles["FarmerBody"])]

    story.append(Paragraph(escape(treatment_heading), styles["FarmerHead"]))
    verified_docs = []
    if guidance_allowed:
        seen = set()
        for retrieval in diagnosis.get("knowledge_retrieval", []) or []:
            for item in retrieval.get("knowledge", []) or []:
                if item.get("verification_status") == "verified":
                    doc_text = str(item.get("document", "")).strip()
                    if doc_text and doc_text.lower() not in seen:
                        seen.add(doc_text.lower())
                        verified_docs.append(doc_text)
    treatment_text = "\n".join(verified_docs[:3]) if verified_docs else no_treatment
    story.append(Paragraph(escape(treatment_text).replace("\n", "<br/>"), styles["FarmerBody"]))

    story.append(Paragraph(escape(weather_heading), styles["FarmerHead"]))
    alerts = weather.get("crop_weather_context", []) or []
    weather_messages = []
    for alert in alerts:
        msg = alert.get("message_bn") if is_bn else alert.get("message_en")
        if msg:
            weather_messages.append(str(msg))
    weather_text = " ".join(dict.fromkeys(weather_messages)) or ("No additional local weather note is available." if not is_bn else "এ মুহূর্তে অতিরিক্ত আবহাওয়ার তথ্য নেই।")
    story.append(Paragraph(escape(weather_text), styles["FarmerBody"]))

    story += [Paragraph(escape(note_heading), styles["FarmerHead"]),
              Paragraph(escape(review_line + " " + generic_note), styles["FarmerBody"]),
              Paragraph(escape("Crop Guardian • Practical help for healthier crops" if not is_bn else "ক্রপ গার্ডিয়ান • সুস্থ ফসলের সহজ সহায়তা"), styles["FarmerSmall"])]
    doc.build(story)
    return buffer.getvalue()
