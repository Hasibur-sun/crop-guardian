import json
import tempfile
import html
import textwrap
from pathlib import Path

import streamlit as st

from crop_guardian_engine import run_crop_guardian
from crop_guardian_reports import load_diagnosis_history, build_diagnosis_pdf


# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
EVAL_DIR = BASE_DIR / "eval"
WEATHER_FILE = EVAL_DIR / "bangladesh_weather_risk.json"
ALERT_FILE = EVAL_DIR / "weather_alerts.json"

st.set_page_config(
    page_title="Crop Guardian | Field Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================================
# 2. BRAND SYSTEM + RESPONSIVE CSS
# =====================================================

st.markdown(
    """
    <style>
    :root {
        --forest: #0A3323;
        --moss: #839958;
        --cream: #F7F4D5;
        --rose: #D3968C;
        --midnight: #105666;
        --paper: #FBFAF1;
        --ink: #183B2C;
        --muted: #586B60;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    #MainMenu, footer, [data-testid="stSidebar"] { display: none; }

    .block-container {
        max-width: 1380px;
        padding: 1.1rem 3.2rem 3.5rem 3.2rem;
    }

    html, body, [class*="css"] {
        font-family: "Trebuchet MS", "Nirmala UI", "Noto Sans Bengali", sans-serif;
    }

    h1, h2, h3, h4 { color: var(--forest) !important; }

    .cg-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 8px 0 17px;
        border-bottom: 1px solid rgba(10,51,35,.20);
        margin-bottom: 24px;
    }

    .cg-logo {
        color: var(--forest);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -1.5px;
        white-space: nowrap;
    }

    .cg-logo span { color: var(--moss); }

    .cg-eyebrow {
        color: var(--moss);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2.8px;
        text-transform: uppercase;
    }

    .cg-hero {
        background:
            radial-gradient(circle at 83% 23%, rgba(131,153,88,.38), transparent 29%),
            radial-gradient(circle at 75% 100%, rgba(211,150,140,.18), transparent 30%),
            var(--forest);
        min-height: 330px;
        border-radius: 3px;
        padding: 42px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: var(--cream);
    }

    .cg-hero:after {
        content: "";
        position: absolute;
        width: 265px;
        height: 265px;
        right: 7%;
        top: 12%;
        border: 1px solid rgba(247,244,213,.22);
        border-radius: 50%;
        box-shadow: 0 0 0 25px rgba(247,244,213,.025), 0 0 0 55px rgba(247,244,213,.025);
        pointer-events: none;
    }

    .cg-hero h1 {
        color: var(--cream) !important;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(42px, 6vw, 76px);
        font-weight: 400;
        line-height: 1.03;
        letter-spacing: -2px;
        max-width: 720px;
        margin: 14px 0;
        position: relative;
        z-index: 1;
    }

    .cg-hero p {
        color: #E5EAD8;
        font-size: 15px;
        line-height: 1.8;
        max-width: 560px;
        position: relative;
        z-index: 1;
        margin-bottom: 0;
    }

    .cg-hero .cg-eyebrow { color: #C5D19D; position: relative; z-index: 1; }

    .cg-hero-art {
        position: absolute;
        right: 12%;
        bottom: -28px;
        color: var(--moss);
        font-family: Georgia, serif;
        font-size: 155px;
        opacity: .27;
        transform: rotate(-15deg);
        z-index: 0;
        pointer-events: none;
    }

    .cg-section { margin-top: 43px; margin-bottom: 18px; }
    .cg-section h2 {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 34px;
        font-weight: 400;
        letter-spacing: -1px;
        margin: 6px 0;
    }

    .cg-muted { color: var(--muted); font-size: 13px; line-height: 1.75; }

    .cg-note {
        background: var(--forest);
        color: var(--cream);
        padding: 29px;
        min-height: 340px;
        border-radius: 3px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
    }

    .cg-note .cg-eyebrow { color: #B8C88C; }
    .cg-note-title {
        color: var(--cream);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 34px;
        line-height: 1.15;
        margin-top: 24px;
    }
    .cg-note p { color: #E1E8D8; font-size: 14px; line-height: 1.85; margin-top: 17px; }
    .cg-note-mark { color: var(--moss); font-family: Georgia, serif; font-size: 58px; text-align: right; }

    .cg-result {
        background: #FFFFFF;
        border: 1px solid rgba(10,51,35,.17);
        border-top: 3px solid var(--moss);
        border-radius: 3px;
        padding: 21px;
        min-height: 130px;
        margin: 8px 0;
    }
    .cg-result-label {
        color: var(--moss);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .cg-result h3 {
        font-family: Georgia, "Times New Roman", serif;
        font-size: 25px;
        font-weight: 400;
        margin: 12px 0 5px;
    }

    .cg-journal {
        background: var(--cream);
        border-left: 4px solid var(--moss);
        padding: 23px;
        min-height: 190px;
        margin-bottom: 12px;
    }
    .cg-number { color: var(--forest); font-family: Georgia, serif; font-size: 42px; }

    .cg-weather-panel {
        background: var(--midnight);
        color: #FFFFFF;
        padding: 23px;
        border-radius: 3px;
    }
    .cg-weather-panel h3 { color: var(--cream) !important; font-family: Georgia, serif; font-weight: 400; }
    .cg-weather-panel p { color: #F0F3E8; line-height: 1.7; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid rgba(10,51,35,.14);
        border-left: 3px solid var(--moss);
        padding: 12px 14px;
        border-radius: 3px;
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    [data-testid="stMetricValue"] { color: var(--forest) !important; }

    .cg-footer {
        margin-top: 55px;
        padding: 25px 0;
        border-top: 1px solid rgba(10,51,35,.20);
        color: var(--muted);
        font-size: 12px;
    }

    /* Native Streamlit controls styled to match the brand. */
    .stSelectbox label, .stFileUploader label, .stRadio label {
        color: var(--forest) !important;
        font-weight: 600;
    }

    div[data-baseweb="select"] > div {
        background: var(--cream) !important;
        color: var(--forest) !important;
        border: 1px solid var(--moss) !important;
        border-radius: 3px !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(247,244,213,.48);
        border: 1px dashed var(--moss);
        border-radius: 3px;
        padding: 14px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,.55) !important;
        border: 0 !important;
    }

    .stButton > button, .stDownloadButton > button {
        background: var(--forest) !important;
        color: var(--cream) !important;
        border: 1px solid var(--forest) !important;
        border-radius: 2px !important;
        min-height: 46px;
        font-weight: 700;
        transition: background .2s ease, border-color .2s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        background: var(--moss) !important;
        border-color: var(--moss) !important;
        color: #FFFFFF !important;
    }

    /* Keep Streamlit alerts readable on the light background. */
    [data-testid="stAlert"] {
        border-radius: 3px;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: #183B2C !important;
    }

    [data-testid="stMarkdownContainer"] a { color: var(--midnight); }
    hr { border-color: rgba(10,51,35,.18) !important; }

    @media (max-width: 768px) {
        .block-container { padding: .7rem 1rem 2rem 1rem; }
        .cg-nav { align-items: flex-start; flex-direction: column; gap: 8px; }
        .cg-logo { font-size: 24px; }
        .cg-hero { min-height: 285px; padding: 25px 20px; }
        .cg-hero h1 { font-size: 43px; letter-spacing: -1.2px; }
        .cg-hero-art { font-size: 100px; right: 3%; }
        .cg-section { margin-top: 30px; }
        .cg-section h2 { font-size: 28px; }
        .cg-note { min-height: 260px; padding: 22px; }
        .cg-note-title { font-size: 30px; }
        .cg-result { padding: 16px; }
        .stButton > button, .stDownloadButton > button { width: 100%; }
        div[role="radiogroup"] { gap: 7px !important; flex-wrap: wrap !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# 3. HELPER FUNCTIONS
# =====================================================

def render_html(markup):
    """Render an HTML fragment without Markdown code-block indentation."""
    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def load_json(path):
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return None


def safe_text(value):
    return html.escape(str(value or ""))


def weather_assessment_label(code, is_bn=False):
    """Convert internal weather screening codes into farmer-facing wording."""
    labels = {
        "limited_favorable_indicators": (
            "Some weather conditions may support disease development",
            "কিছু আবহাওয়াগত অবস্থা রোগের বিস্তারে সহায়ক হতে পারে",
        ),
        "weather_context_only": (
            "Weather information available; risk is not confirmed",
            "আবহাওয়ার তথ্য পাওয়া গেছে; ঝুঁকি নিশ্চিত নয়",
        ),
        "research_conditions_not_met": (
            "The selected weather conditions were not fully observed",
            "নির্বাচিত আবহাওয়াগত শর্তগুলো পুরোপুরি পাওয়া যায়নি",
        ),
        "insufficient_temporal_resolution": (
            "There is not enough detailed weather data for this assessment",
            "এই মূল্যায়নের জন্য পর্যাপ্ত বিস্তারিত আবহাওয়ার তথ্য নেই",
        ),
        "exploratory_weather_screen": (
            "Weather conditions are being monitored",
            "আবহাওয়ার অবস্থা পর্যবেক্ষণ করা হচ্ছে",
        ),
        "no_strong_signal": (
            "No strong weather warning",
            "আবহাওয়ায় বড় ধরনের সতর্ক সংকেত পাওয়া যায়নি",
        ),
        "weather_context": (
            "Weather information available",
            "আবহাওয়ার তথ্য পাওয়া গেছে",
        ),
    }
    key = str(code or "").strip().lower()
    pair = labels.get(key)
    if pair:
        return pair[1] if is_bn else pair[0]
    return "Weather information available" if not is_bn else "আবহাওয়ার তথ্য পাওয়া গেছে"


def weather_interpretation(code, is_bn=False):
    messages = {
        "limited_favorable_indicators": (
            "Some of the observed weather conditions may favor disease development. This does not mean the crop is infected. Check the leaves regularly.",
            "পর্যবেক্ষিত কিছু আবহাওয়াগত অবস্থা রোগের বিস্তারে সহায়ক হতে পারে। তবে এর অর্থ এই নয় যে গাছে রোগ হয়েছে। নিয়মিত পাতা পরীক্ষা করুন।",
        ),
        "weather_context_only": (
            "Weather information is available, but it is not enough on its own to estimate disease risk. Keep monitoring your plants.",
            "আবহাওয়ার তথ্য পাওয়া গেছে, তবে শুধু এই তথ্য দিয়ে রোগের ঝুঁকি নির্ধারণ করা যায় না। গাছ নিয়মিত পর্যবেক্ষণ করুন।",
        ),
        "research_conditions_not_met": (
            "The full set of weather conditions used for this screening was not observed. Continue normal field checks.",
            "এই পর্যবেক্ষণে প্রয়োজনীয় সব আবহাওয়াগত শর্ত পাওয়া যায়নি। নিয়মিত ফসল পরীক্ষা চালিয়ে যান।",
        ),
        "insufficient_temporal_resolution": (
            "The available data does not show how long the leaves stayed wet. Check the plants directly for symptoms.",
            "পাতা কতক্ষণ ভেজা ছিল, এই তথ্য তা জানায় না। রোগের লক্ষণ আছে কি না সরাসরি গাছ পরীক্ষা করুন।",
        ),
        "exploratory_weather_screen": (
            "These are early weather observations, not a confirmed disease-risk result. Keep monitoring your crop.",
            "এগুলো প্রাথমিক আবহাওয়ার পর্যবেক্ষণ, নিশ্চিত রোগ-ঝুঁকির ফল নয়। ফসল পর্যবেক্ষণ করুন।",
        ),
        "no_strong_signal": (
            "The selected weather indicators were limited during this period. Continue checking your crop regularly.",
            "এই সময়ে নির্বাচিত আবহাওয়ার সূচকগুলো সীমিত ছিল। নিয়মিত ফসল পরীক্ষা করুন।",
        ),
    }
    pair = messages.get(str(code or "").strip().lower())
    if pair:
        return pair[1] if is_bn else pair[0]
    return "Weather observations are for general guidance only, not disease confirmation." if not is_bn else "আবহাওয়ার তথ্য সাধারণ ধারণার জন্য; এটি রোগ নিশ্চিত করে না।"


def weather_indicator_label(key, is_bn=False):
    labels = {
        "average_temperature": ("Average temperature", "গড় তাপমাত্রা"),
        "average_temperature_c": ("Average temperature", "গড় তাপমাত্রা"),
        "average_minimum_temperature": ("Average minimum temperature", "গড় সর্বনিম্ন তাপমাত্রা"),
        "average_daily_temperature": ("Average daily temperature", "গড় দৈনিক তাপমাত্রা"),
        "average_humidity": ("Average humidity", "গড় আর্দ্রতা"),
        "average_humidity_percent": ("Average humidity", "গড় আর্দ্রতা"),
        "average_daily_humidity": ("Average daily humidity", "গড় দৈনিক আর্দ্রতা"),
        "maximum_humidity": ("Highest humidity", "সর্বোচ্চ আর্দ্রতা"),
        "minimum_humidity": ("Lowest humidity", "সর্বনিম্ন আর্দ্রতা"),
        "total_rainfall_mm": ("Total rainfall", "মোট বৃষ্টিপাত"),
        "rainfall_mm": ("Rainfall", "বৃষ্টিপাত"),
        "rainy_hours": ("Hours with rain", "বৃষ্টির সময়"),
        "hours_humidity_above_90": ("Hours with very high humidity", "অতি বেশি আর্দ্রতার সময়"),
        "hours_humidity_above_85": ("Hours with high humidity", "বেশি আর্দ্রতার সময়"),
        "days_humidity_above_85": ("Days with high humidity", "বেশি আর্দ্রতার দিন"),
        "combined_temperature_humidity_hours": ("Hours with combined warm and humid conditions", "উষ্ণ ও আর্দ্র আবহাওয়ার সময়"),
        "hours_temperature_16_20": ("Hours in the monitored temperature range", "পর্যবেক্ষিত তাপমাত্রার সীমার সময়"),
        "hours_with_rh_above_90": ("Hours with very high humidity", "অতি বেশি আর্দ্রতার সময়"),
    }
    pair = labels.get(str(key).strip().lower())
    return (pair[1] if is_bn else pair[0]) if pair else None


def format_weather_value(key, value, is_bn=False):
    """Format weather values using the unit implied by the measurement."""
    if value is None:
        return "পাওয়া যায়নি" if is_bn else "Not available"

    key_lower = str(key).strip().lower()

    # These fields count hourly observations; they are not measurements
    # of temperature, humidity percentage, or rainfall amount.
    hour_count_keys = {
        "rainy_hours",
        "hours_humidity_above_90",
        "hours_humidity_above_85",
        "combined_temperature_humidity_hours",
        "hours_temperature_16_20",
        "hours_with_rh_above_90",
    }
    day_count_keys = {"days_humidity_above_85"}

    if key_lower in hour_count_keys:
        unit = "ঘণ্টা" if is_bn else "hours"
        return f"{value} {unit}"

    if key_lower in day_count_keys:
        unit = "দিন" if is_bn else "days"
        return f"{value} {unit}"

    if "humidity" in key_lower or key_lower.startswith("rh"):
        return f"{value}%"

    if "temperature" in key_lower or key_lower.endswith("_c"):
        return f"{value} °C"

    if "rainfall" in key_lower or key_lower == "rainfall_mm":
        return f"{value} mm"

    return str(value)


def render_weather_indicators(indicators, is_bn=False):
    """Show only recognized, human-readable weather indicators; never raw JSON keys."""
    if not isinstance(indicators, dict):
        return
    display_items = []
    for key, value in indicators.items():
        label = weather_indicator_label(key, is_bn)
        if label is not None and isinstance(value, (int, float, str)):
            display_items.append(
                (label, format_weather_value(key, value, is_bn))
            )
    if display_items:
        cols = st.columns(min(3, len(display_items)))
        for index, (label, value) in enumerate(display_items):
            with cols[index % len(cols)]:
                st.metric(label, value)


def show_prediction(prediction):
    disease = safe_text(str(prediction.get("disease", "Unknown")).replace("_", " ").title())
    source = str(prediction.get("source_model", "")).lower()
    model_label = "প্রথম AI পরীক্ষা" if source.startswith("efficientnet") and is_bn else (
        "দ্বিতীয় AI পরীক্ষা" if is_bn else "AI assessment 1" if source.startswith("efficientnet") else "AI assessment 2"
    )
    score = prediction.get("model_score")
    score_note = "এটি নিশ্চিত হওয়ার পরিমাপ নয়" if is_bn else "This is an AI score, not a confirmed probability."
    score_text = f"{score:.1%}" if isinstance(score, (int, float)) else ("পাওয়া যায়নি" if is_bn else "Not available")

    render_html(f"""
    <div class="cg-result">
        <div class="cg-result-label">{safe_text(model_label)}</div>
        <h3>{disease}</h3>
        <p class="cg-muted">{('AI স্কোর' if is_bn else 'AI score')}: {score_text}. {score_note}</p>
    </div>
    """)


def render_hero(eyebrow, title, second_line, description, symbol="❋"):
    render_html(f"""
    <section class="cg-hero">
        <div class="cg-eyebrow">{safe_text(eyebrow)}</div>
        <h1>{title}<br><span style="color:#839958">{second_line}</span></h1>
        <p>{description}</p>
        <div class="cg-hero-art">{symbol}</div>
    </section>
    """)


# =====================================================
# 4. TOP NAVIGATION + LANGUAGE
# =====================================================

nav_col, lang_col = st.columns([4, 1])

with nav_col:
    render_html("""
    <div class="cg-nav">
        <div class="cg-logo">crop guardian<span>.</span></div>
        <div class="cg-eyebrow">FIELD INTELLIGENCE · BANGLADESH</div>
    </div>
    """)

with lang_col:
    language = st.selectbox(
        "Language / ভাষা",
        ["English", "বাংলা"],
        label_visibility="collapsed",
        key="cg_language",
    )

is_bn = language == "বাংলা"


# =====================================================
# 5. NAVIGATION
# =====================================================

page_labels = (
    ["01 · রোগ পরীক্ষা", "02 · আবহাওয়া", "03 · ইতিহাস", "04 · আমাদের সম্পর্কে"]
    if is_bn else
    ["01 · Check a crop", "02 · Weather", "03 · History", "04 · How it helps"]
)

page = st.radio(
    "Navigation",
    page_labels,
    horizontal=True,
    label_visibility="collapsed",
    key="cg_navigation_v2",
)

st.markdown("---")


# =====================================================
# 6. DIAGNOSIS PAGE
# =====================================================

if page in ("01 · Check a crop", "01 · রোগ পরীক্ষা", "01 · Diagnose"):
    if is_bn:
        render_hero(
            "ফসলের যত্নে নতুন দৃষ্টিভঙ্গি",
            "আপনার ফসলকে জানুন।",
            "ফসলকে সুরক্ষিত রাখুন।",
            "কৃত্রিম বুদ্ধিমত্তা, কৃষি জ্ঞান এবং আবহাওয়ার তথ্যের সমন্বয়ে ফসলের স্বাস্থ্য পর্যবেক্ষণ।",
        )
        section_title = "আপনার গাছটি পরীক্ষা করি।"
        section_description = "আক্রান্ত পাতার একটি পরিষ্কার ছবি আপলোড করুন।"
        upload_heading = "আপনার ফসলের নমুনা"
        crop_prompt = "ফসল নির্বাচন করুন"
        upload_prompt = "পাতার ছবি আপলোড করুন"
        button_label = "ফসল পরীক্ষা করুন →"
    else:
        render_hero(
            "A NEW WAY TO CARE FOR YOUR CROPS",
            "Know your crops.",
            "Protect your harvest.",
            "Where artificial intelligence meets agricultural knowledge and local weather intelligence.",
        )
        section_title = "Let's examine your plant."
        section_description = (
            "Begin with a clear photograph of an affected leaf. "
            "Our AI models will examine it alongside agricultural knowledge."
        )
        upload_heading = "Your field sample"
        crop_prompt = "Select your crop"
        upload_prompt = "Upload leaf photograph"
        button_label = "Examine my crop →"

    render_html(f"""
    <div class="cg-section">
        <div class="cg-eyebrow">01 / PLANT HEALTH</div>
        <h2>{section_title}</h2>
        <p class="cg-muted">{section_description}</p>
    </div>
    """)

    left, right = st.columns([1.15, 0.85], gap="large")

    crop_options = {
        "Potato": "potato",
        "Tomato": "tomato",
        "Rice": "rice",
        "Brinjal": "brinjal",
        "Jute": "jute",
    }

    crop_labels_bn = {
        "আলু": "potato",
        "টমেটো": "tomato",
        "ধান": "rice",
        "বেগুন": "brinjal",
        "পাট": "jute",
    }

    with left:
        # Use a real Streamlit container. Do not split an HTML div
        # across separate st.markdown calls.
        with st.container(border=True):
            st.markdown(f"### {upload_heading}")

            if is_bn:
                selected_label = st.selectbox(
                    crop_prompt,
                    list(crop_labels_bn.keys()),
                    key="cg_crop_bn",
                )
                selected_crop = crop_labels_bn[selected_label]
            else:
                selected_label = st.selectbox(
                    crop_prompt,
                    list(crop_options.keys()),
                    key="cg_crop_en",
                )
                selected_crop = crop_options[selected_label]

            uploaded_file = st.file_uploader(
                upload_prompt,
                type=["jpg", "jpeg", "png"],
                help="Use a clear photograph with visible leaf symptoms.",
                key="cg_leaf_upload",
            )

            if uploaded_file:
                st.image(
                    uploaded_file,
                    caption=(
                        "আপলোড করা পাতার ছবি" if is_bn
                        else "Your uploaded field sample"
                    ),
                    width="stretch",
                )

            analyze_button = st.button(
                button_label,
                type="primary",
                use_container_width=True,
                disabled=uploaded_file is None,
                key="cg_analyze_button",
            )

    with right:
        render_html("""
        <div class="cg-note">
            <div>
                <div class="cg-eyebrow">FIELD NOTE · 001</div>
                <div class="cg-note-title">Every leaf<br>tells a story.</div>
                <p>
                    A photograph can help reveal signs of plant stress
                    and disease. Good lighting and a focused image help
                    our models examine visible symptoms.
                </p>
            </div>
            <div class="cg-note-mark">❋</div>
        </div>
        """)

    # -----------------------------------------
    # RUN THE EXISTING BACKEND
    # -----------------------------------------

    if analyze_button and uploaded_file:
        temp_path = None

        try:
            image_bytes = uploaded_file.getvalue()
            suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name

            with st.spinner(
                "Examining your crop... Running AI diagnosis and knowledge retrieval."
            ):
                location_file = BASE_DIR / "data" / "weather_location.json"
                saved_field_location = load_json(location_file) or {}
                field_coordinates = {
                    "latitude": saved_field_location.get("latitude", 23.8103),
                    "longitude": saved_field_location.get("longitude", 90.4125),
                    "source": saved_field_location.get("source", "Dhaka default"),
                }
                report = run_crop_guardian(
                    temp_path,
                    selected_crop,
                    original_filename=uploaded_file.name,
                    field_coordinates=field_coordinates,
                )

            st.session_state["crop_report"] = report
            st.session_state["crop_image_name"] = uploaded_file.name
            st.session_state["crop_image_bytes"] = image_bytes
            st.session_state["crop_selected_crop"] = selected_crop

            st.success(
                "Your crop examination is complete."
                if not is_bn else "ফসল পরীক্ষা সম্পন্ন হয়েছে।"
            )

        except Exception as error:
            st.error(f"Analysis failed: {error}")

        finally:
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()

    # -----------------------------------------
    # DISPLAY RESULTS
    # -----------------------------------------

    if "crop_report" in st.session_state:
        report = st.session_state["crop_report"]
        diagnosis = report.get("diagnosis", {})
        weather = report.get("weather_intelligence", {})
        safety = report.get("safety", {})

        image_validation = diagnosis.get("image_validation", {})
        if image_validation and not image_validation.get("valid_for_diagnosis", True):
            validation_reason = image_validation.get("reason", "Please upload a clear crop-leaf photograph.")
            st.error(validation_reason if not is_bn else "ছবিটি পরীক্ষা করার উপযোগী নয়। পরিষ্কার পাতার ছবি দিন।")
            st.info(
                "Try again with a clear, well-lit photo of one crop leaf."
                if not is_bn else
                "ভালো আলোতে একটি ফসলের পাতার পরিষ্কার ছবি তুলে আবার চেষ্টা করুন।"
            )
            st.stop()

        st.markdown("---")
        render_html("""
        <div class="cg-section">
            <div class="cg-eyebrow">02 / ANALYSIS</div>
            <h2>Your field report.</h2>
        </div>
        """)


        # ----------------------------------
        # SIMPLE FARMER-FACING REPORT
        # ----------------------------------
        predictions = diagnosis.get("model_predictions", []) or []
        selected_crop = str(report.get("selected_crop", "crop")).replace("_", " ").title()
        status = diagnosis.get("hybrid_status", diagnosis.get("status", "uncertain"))
        needs_review = bool(safety.get("human_review_required", diagnosis.get("needs_review", True)))
        guidance_allowed = bool(diagnosis.get("farmer_guidance_allowed", False)) and not needs_review

        def _friendly_disease(value):
            return str(value or "").replace("_", " ").replace("  ", " ").title()

        disease_names = [
            _friendly_disease(item.get("disease"))
            for item in predictions
            if item.get("disease") and str(item.get("disease")).lower() not in {"unknown", "healthy"}
        ]
        same_disease = bool(disease_names) and len(set(x.lower() for x in disease_names)) == 1
        healthy_only = bool(predictions) and all(
            str(item.get("disease", "")).strip().lower() == "healthy" for item in predictions
        )

        if is_bn:
            st.markdown("## আপনার ফসলের স্বাস্থ্য প্রতিবেদন")
        else:
            st.markdown("## Your plant health report")

        if status == "crop_mismatch":
            st.error("ছবির ফসলটি আপনার নির্বাচিত ফসলের সঙ্গে মিলছে না। সঠিক ফসল নির্বাচন করে পরিষ্কার ছবি দিন।" if is_bn else
                     "The plant in the photo may not match the crop you selected. Please check the crop and upload a clear photo.")
        elif healthy_only and not needs_review:
            st.success("ছবিতে রোগের স্পষ্ট লক্ষণ পাওয়া যায়নি। গাছ পর্যবেক্ষণ চালিয়ে যান।" if is_bn else
                       "No clear disease symptoms were identified in this photo. Keep monitoring the plant.")
        elif same_disease and status == "model_agreement":
            st.warning((f"সম্ভাব্য সমস্যা: {_friendly_disease(disease_names[0])}. এটি নিশ্চিত রোগ নির্ণয় নয়।" if is_bn else
                        f"Possible problem: {_friendly_disease(disease_names[0])}. This is not a confirmed diagnosis."))
        else:
            st.warning("ছবি থেকে সমস্যাটি নিশ্চিতভাবে বোঝা যায়নি। নতুন পরিষ্কার ছবি তুলুন অথবা কৃষি কর্মকর্তার পরামর্শ নিন।" if is_bn else
                       "We could not identify the problem confidently from this photo. Try a clearer photo or ask an agricultural officer.")

        if same_disease and status == "model_agreement":
            st.markdown("### " + ("এটি কেন হতে পারে" if is_bn else "What may be causing it"))
            st.write("পাতার লক্ষণ এই সমস্যার সঙ্গে মিলে যেতে পারে। আবহাওয়া, গাছের অবস্থা এবং মাঠের অন্যান্য লক্ষণও বিবেচনা করা প্রয়োজন।" if is_bn else
                     "The leaf symptoms are consistent with this condition. Weather, plant condition and symptoms on other leaves also matter.")
        elif healthy_only:
            st.markdown("### " + ("এখন কী করবেন" if is_bn else "What to do now"))
            st.write("গাছ নিয়মিত দেখুন। নতুন দাগ, হলদে ভাব বা পাতা শুকিয়ে যাওয়া দেখা দিলে আবার ছবি তুলুন।" if is_bn else
                     "Keep checking the plant. If new spots, yellowing or drying appear, take another photo for review.")

        # Only display source-backed knowledge as practical guidance when the
        # existing RAG verification gate explicitly permits it.
        retrievals = diagnosis.get("knowledge_retrieval", []) or []
        verified_docs = []
        if guidance_allowed:
            seen_docs = set()
            for retrieval in retrievals:
                for item in retrieval.get("knowledge", []) or []:
                    if item.get("verification_status") != "verified":
                        continue
                    document = str(item.get("document", "")).strip()
                    url = str(item.get("source_url", "")).strip()
                    key = (document.lower(), url.lower())
                    if document and key not in seen_docs:
                        seen_docs.add(key)
                        verified_docs.append((document, url))

        st.markdown("### " + ("করণীয়" if is_bn else "What you can do"))
        if verified_docs:
            for document, url in verified_docs[:3]:
                st.write(document)
                if url:
                    st.markdown((f"[তথ্যসূত্র দেখুন]({url})" if is_bn else f"[View source]({url})"))
        else:
            st.info("এই ফলাফলের ভিত্তিতে নিরাপদ ও যাচাইকৃত চিকিৎসা বা ওষুধের পরামর্শ দেওয়া যাচ্ছে না। স্থানীয় কৃষি কর্মকর্তার সঙ্গে কথা বলুন।" if is_bn else
                    "We do not yet have verified treatment or medicine instructions for this result. Please ask a local agricultural officer before applying any pesticide or medicine.")

        st.markdown("### " + ("আবহাওয়ার সংক্ষিপ্ত তথ্য" if is_bn else "Weather in your area"))
        crop_alerts = weather.get("crop_weather_context", []) or []
        useful_weather = []
        for alert in crop_alerts:
            message = alert.get("message_bn") if is_bn else alert.get("message_en")
            if message:
                useful_weather.append(str(message))
        if useful_weather:
            for message in dict.fromkeys(useful_weather):
                st.write(message)
        else:
            st.caption("এই মুহূর্তে অতিরিক্ত আবহাওয়ার তথ্য নেই।" if is_bn else "No additional local weather note is available right now.")

        st.info("এটি ছবির ভিত্তিতে প্রাথমিক সহায়তা, নিশ্চিত রোগ নির্ণয় নয়। সমস্যা বাড়লে বা ওষুধ ব্যবহারের আগে স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।" if is_bn else
                "This is an initial photo-based assessment, not a confirmed diagnosis. If the problem spreads, or before using a pesticide, consult a local agricultural officer.")

        # Technical JSON remains available for support/debugging, but is not the primary farmer report.
        with st.expander("কারিগরি প্রতিবেদন" if is_bn else "Technical report"):
            st.download_button(
                "JSON ডাউনলোড" if is_bn else "Download technical JSON",
                data=json.dumps(report, indent=2, ensure_ascii=False),
                file_name="crop_guardian_technical_report.json",
                mime="application/json",
                use_container_width=True,
            )

        try:
            pdf_bytes = build_diagnosis_pdf(report, language=language)
            st.download_button(
                "সহজ প্রতিবেদন ডাউনলোড করুন (PDF) ↓" if is_bn else "Download simple crop report (PDF) ↓",
                data=pdf_bytes,
                file_name=f"crop_guardian_{report.get('selected_crop', 'field')}_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="cg_current_report_pdf_simple",
            )
        except Exception as pdf_error:
            st.warning(("PDF তৈরি করা যায়নি: " if is_bn else "PDF could not be generated: ") + str(pdf_error))


# =====================================================
# 7. WEATHER PAGE — FARMER-FRIENDLY VIEW
# =====================================================

elif page in ("02 · Weather", "02 · আবহাওয়া", "02 · Field intelligence"):
    if is_bn:
        render_hero(
            "আপনার এলাকার আবহাওয়া",
            "আবহাওয়া বুঝুন।",
            "ফসলের যত্ন নিন।",
            "সাম্প্রতিক আবহাওয়ার তথ্য দেখে ফসলের দিকে কখন বেশি নজর দিতে হবে তা বুঝুন।",
            symbol="☼",
        )
        weather_heading = "সাম্প্রতিক আবহাওয়ার তথ্য"
        no_weather_text = "আবহাওয়ার প্রতিবেদন পাওয়া যায়নি। পরে আবার চেষ্টা করুন।"
        weather_note = "এই তথ্য আবহাওয়ার সাধারণ ধারণা দেয়। এটি কোনো রোগ নিশ্চিত করে না।"
    else:
        render_hero(
            "LOCAL WEATHER FOR YOUR CROPS",
            "Read the weather.",
            "Care for your field.",
            "Simple weather observations to help you decide when to pay closer attention to your crops.",
            symbol="☼",
        )
        weather_heading = "Recent weather observations"
        no_weather_text = "The weather report is not available yet. Please try again later."
        weather_note = "These observations provide general weather context. They do not confirm a plant disease."

    # Farmer-selected field coordinates. NASA POWER returns gridded estimates, not farm sensors.
    st.markdown("### " + ("জমির অবস্থান" if is_bn else "Your field location"))
    location_file = BASE_DIR / "data" / "weather_location.json"
    saved_location = load_json(location_file) or {}
    default_lat = float(saved_location.get("latitude", 23.8103))
    default_lon = float(saved_location.get("longitude", 90.4125))

    with st.form("cg_field_location_form"):
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            field_latitude = st.number_input(
                "অক্ষাংশ (Latitude)" if is_bn else "Latitude",
                min_value=20.5, max_value=26.8, value=max(20.5, min(26.8, default_lat)),
                step=0.0001, format="%.4f"
            )
        with loc_col2:
            field_longitude = st.number_input(
                "দ্রাঘিমাংশ (Longitude)" if is_bn else "Longitude",
                min_value=88.0, max_value=92.8, value=max(88.0, min(92.8, default_lon)),
                step=0.0001, format="%.4f"
            )
        refresh_weather = st.form_submit_button(
            "আবহাওয়া হালনাগাদ করুন" if is_bn else "Update weather for this location",
            type="primary"
        )

    if refresh_weather:
        try:
            with st.spinner("NASA POWER থেকে আবহাওয়ার তথ্য আনা হচ্ছে..." if is_bn else "Fetching daily and hourly weather from NASA POWER..."):
                import weather as daily_weather
                import weather_hourly as hourly_weather
                import bangladesh_weather_risk as risk_engine

                # Fetch both datasets using exactly the same selected coordinates.
                daily_payload = daily_weather.fetch_weather(
                    field_latitude, field_longitude, *daily_weather.get_default_dates()
                )
                daily_records = daily_weather.process_weather(daily_payload)
                if not daily_records:
                    raise RuntimeError("NASA POWER returned no daily weather records.")
                daily_weather.save_weather(daily_records, field_latitude, field_longitude)

                hourly_payload, hourly_start, hourly_end = hourly_weather.fetch_hourly(
                    field_latitude, field_longitude
                )
                hourly_records = hourly_weather.process_hourly(hourly_payload)
                if not hourly_records:
                    raise RuntimeError("NASA POWER returned no hourly weather records.")
                hourly_weather.save_hourly(hourly_records)

                risk_engine.main(field_latitude, field_longitude)

                # Persist coordinates only after both weather feeds and screening succeed.
                location_file.parent.mkdir(parents=True, exist_ok=True)
                location_file.write_text(
                    json.dumps({
                        "latitude": float(field_latitude),
                        "longitude": float(field_longitude),
                        "source": "farmer_selected_field",
                        "updated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
                    }, indent=2),
                    encoding="utf-8",
                )

            st.success("আবহাওয়া হালনাগাদ হয়েছে।" if is_bn else "Weather updated for the selected field location.")
            st.rerun()
        except Exception as exc:
            st.error(("আবহাওয়া হালনাগাদ করা যায়নি: " if is_bn else "Could not update weather: ") + str(exc))

    weather_data = load_json(WEATHER_FILE)
    alert_data = load_json(ALERT_FILE)

    render_html(f"""
    <div class="cg-section">
        <div class="cg-eyebrow">{('আপনার ফসল' if is_bn else 'FOR YOUR CROPS')}</div>
        <h2>{safe_text(weather_heading)}</h2>
        <p class="cg-muted">{safe_text(weather_note)}</p>
    </div>
    """)

    if weather_data:
        # Show only friendly, recognized measurements. Do not expose JSON or internal keys.
        summary = weather_data.get("summary", {}) if isinstance(weather_data, dict) else {}
        if not isinstance(summary, dict):
            summary = {}
        friendly_summary = [
            (("গড় তাপমাত্রা" if is_bn else "Average temperature"), summary.get("average_temperature_c", summary.get("average_temperature")), "°C"),
            (("গড় আর্দ্রতা" if is_bn else "Average humidity"), summary.get("average_humidity_percent", summary.get("average_humidity")), "%"),
            (("মোট বৃষ্টিপাত" if is_bn else "Total rainfall"), summary.get("total_rainfall_mm", summary.get("total_rainfall")), "mm"),
        ]
        available_summary = [(label, value, unit) for label, value, unit in friendly_summary if isinstance(value, (int, float))]
        if available_summary:
            metric_cols = st.columns(len(available_summary))
            for col, (label, value, unit) in zip(metric_cols, available_summary):
                with col:
                    st.metric(label, f"{value:.1f} {unit}")

        results = weather_data.get("screening_results", [])
        if not results and isinstance(weather_data.get("crop_weather_context"), list):
            results = weather_data["crop_weather_context"]

        if results:
            st.markdown("### ফসলভিত্তিক আবহাওয়ার খোঁজ" if is_bn else "### What the weather may mean for each crop")
            for item in results:
                crop_name = str(item.get("crop", "Crop")).replace("_", " ").title()
                disease_name = str(item.get("disease", "crop health")).replace("_", " ").title()
                assessment = weather_assessment_label(item.get("assessment"), is_bn)
                assessment_code = item.get("assessment", "")
                explanation = weather_interpretation(assessment_code, is_bn)
                with st.container(border=True):
                    st.markdown(f"#### {safe_text(crop_name)} · {safe_text(disease_name)}")
                    st.markdown(f"**{safe_text(assessment)}**")
                    st.write(explanation)
                    render_weather_indicators(item.get("observed_indicators", {}), is_bn)
        else:
            st.info(no_weather_text)
    else:
        st.info(no_weather_text)

    if alert_data and alert_data.get("alerts"):
        st.markdown("### আবহাওয়ার পরামর্শ" if is_bn else "### Weather notes")
        for alert in alert_data.get("alerts", []):
            crop_name = str(alert.get("crop", "Crop")).replace("_", " ").title()
            disease_name = str(alert.get("disease", "crop health")).replace("_", " ").title()
            friendly_level = weather_assessment_label(alert.get("alert_level"), is_bn)
            message = alert.get("message_bn", "") if is_bn else alert.get("message_en", "")
            with st.container(border=True):
                st.markdown(f"**{safe_text(crop_name)} · {safe_text(disease_name)}**")
                st.markdown(f"{safe_text(friendly_level)}")
                if message:
                    st.write(message)

    st.caption(
        "NASA POWER-এর আবহাওয়ার তথ্য গ্রিডভিত্তিক; এটি সরাসরি আপনার জমির মাপ নয়।" if is_bn
        else "Weather data comes from a regional grid and may differ from conditions in your own field."
    )


# =====================================================
# 8. ABOUT PAGE — SIMPLE EXPLANATION
# =====================================================

elif page in ("03 · History", "03 · ইতিহাস", "03 · Diagnosis History"):
    if is_bn:
        render_hero(
            "আপনার আগের পরীক্ষা",
            "রোগ পরীক্ষার ইতিহাস।",
            "প্রতিবেদন ফিরে দেখুন।",
            "আগে সংরক্ষিত ফসল পরীক্ষার প্রতিবেদন দেখুন এবং PDF ডাউনলোড করুন।",
            symbol="▤",
        )
        st.markdown("### সংরক্ষিত পরীক্ষার তালিকা")
    else:
        render_hero(
            "YOUR PREVIOUS EXAMINATIONS",
            "Diagnosis history.",
            "Reports in one place.",
            "Review saved crop examinations and download a PDF copy of each report.",
            symbol="▤",
        )
        st.markdown("### Saved examinations")

    history_items = load_diagnosis_history(EVAL_DIR)
    if not history_items:
        st.info("এখনও কোনো প্রতিবেদন সংরক্ষিত হয়নি।" if is_bn else "No saved diagnosis reports were found yet.")
    else:
        crop_values = sorted({item["crop"] for item in history_items})
        crop_filter_options = (["সব ফসল"] + crop_values) if is_bn else (["All crops"] + crop_values)
        selected_filter = st.selectbox(
            "ফসল বাছাই করুন" if is_bn else "Filter by crop",
            crop_filter_options,
            key="cg_history_crop_filter",
        )
        all_label = "সব ফসল" if is_bn else "All crops"
        filtered_items = history_items if selected_filter in (all_label, "All crops") else [
            item for item in history_items if item["crop"] == selected_filter
        ]
        st.caption(
            f"মোট প্রতিবেদন: {len(filtered_items)}" if is_bn
            else f"Reports found: {len(filtered_items)}"
        )
        for index, item in enumerate(filtered_items):
            report_data = item["report"]
            status_text = item["status"].replace("_", " ").title()
            date_text = item["modified"].strftime("%Y-%m-%d %H:%M")
            title_text = f"{item['crop'].title()} · {item['image']}"
            with st.expander(f"{title_text} — {date_text}", expanded=(index == 0)):
                st.write(("অবস্থা: " if is_bn else "Status: ") + status_text)
                st.write(("বিশেষজ্ঞ যাচাই প্রয়োজন: " if is_bn else "Expert review required: ") + ("হ্যাঁ" if item["needs_review"] and is_bn else "না" if is_bn else "Yes" if item["needs_review"] else "No"))
                diag = report_data.get("diagnosis", {}) or {}
                predictions = diag.get("model_predictions", []) or []
                if predictions:
                    st.markdown("**" + ("AI পূর্বাভাস" if is_bn else "AI findings") + "**")
                    st.dataframe([
                        {
                            "মডেল" if is_bn else "Model": p.get("source_model", "Unknown"),
                            "ফসল" if is_bn else "Crop": p.get("crop", "Unknown"),
                            "ফলাফল" if is_bn else "Finding": p.get("disease", "Unknown"),
                            "AI score" : p.get("model_score", p.get("confidence")),
                        } for p in predictions
                    ], use_container_width=True, hide_index=True)
                try:
                    pdf_data = build_diagnosis_pdf(report_data, language=language)
                    st.download_button(
                        "PDF ডাউনলোড করুন" if is_bn else "Download this PDF",
                        data=pdf_data,
                        file_name=f"crop_guardian_{item['crop']}_{index + 1}.pdf",
                        mime="application/pdf",
                        key=f"cg_history_pdf_{item['path'].name}",
                    )
                except Exception as pdf_error:
                    st.error(("PDF তৈরি করা যায়নি: " if is_bn else "PDF generation failed: ") + str(pdf_error))
                with st.expander("সম্পূর্ণ JSON প্রতিবেদন" if is_bn else "View complete JSON report"):
                    st.json(report_data)

elif page in ("03 · How it helps", "03 · আমাদের সম্পর্কে", "03 · About"):
    if is_bn:
        render_hero(
            "ফসলের পাশে সহজ সহায়তা",
            "ফসলকে বুঝুন।",
            "যত্নে রাখুন।",
            "গাছের ছবি, কৃষি বিষয়ক তথ্য ও আবহাওয়ার সাধারণ তথ্য এক জায়গায়।",
        )
        about_title = "কীভাবে এটি আপনাকে সাহায্য করে"
        about_intro = "ব্যবহার করা সহজ—শুধু কয়েকটি ধাপ অনুসরণ করুন।"
        steps = [
            ("01", "ছবি তুলুন", "গাছের পাতার পরিষ্কার ছবি তুলুন বা আপলোড করুন।"),
            ("02", "ফলাফল বুঝুন", "ছবিতে কী দেখা যাচ্ছে এবং কোন বিষয়ে আরও যাচাই দরকার তা জানুন।"),
            ("03", "ফসলের খোঁজ রাখুন", "আবহাওয়ার তথ্য ও কৃষি বিষয়ক সহায়ক তথ্য দেখে নিয়মিত ফসল পর্যবেক্ষণ করুন।"),
        ]
        promise_title = "আমাদের কথা"
        promise = "Crop Guardian আপনাকে প্রাথমিক ধারণা দিতে সাহায্য করে। এটি কৃষি কর্মকর্তা, বিশেষজ্ঞ বা পরীক্ষাগারের বিকল্প নয়।"
    else:
        render_hero(
            "PRACTICAL HELP FOR EVERY GROWER",
            "Know your crop.",
            "Care with confidence.",
            "Leaf photographs, useful crop information and local weather context—together in one simple place.",
        )
        about_title = "How Crop Guardian helps"
        about_intro = "A simple process, designed for everyday use."
        steps = [
            ("01", "Take a photo", "Upload a clear photograph of a crop leaf."),
            ("02", "Understand the result", "See what the photo checks found and where more checking may be needed."),
            ("03", "Keep watching your crops", "Use weather notes and helpful crop information as you monitor your field."),
        ]
        promise_title = "A note about the results"
        promise = "Crop Guardian provides an initial AI-assisted screening. It does not replace an agricultural officer, expert examination or laboratory testing."

    render_html(f"""
    <div class="cg-section">
        <div class="cg-eyebrow">{('সহজ ব্যবহার' if is_bn else 'MADE TO BE SIMPLE')}</div>
        <h2>{safe_text(about_title)}</h2>
        <p class="cg-muted">{safe_text(about_intro)}</p>
    </div>
    """)

    step_cols = st.columns(3)
    for col, (number, title, description) in zip(step_cols, steps):
        with col:
            render_html(f"""
            <div class="cg-journal">
                <div class="cg-number">{number}</div>
                <h3>{safe_text(title)}</h3>
                <p class="cg-muted">{safe_text(description)}</p>
            </div>
            """)

    st.markdown(f"### {promise_title}")
    st.info(promise)


# =====================================================
# 9. FOOTER
# =====================================================

render_html(f"""
<div class="cg-footer">
    <div class="cg-logo">crop guardian<span>.</span></div>
    <p>{'ফসলের যত্নে সহজ সহায়তা · বাংলাদেশ' if is_bn else 'PRACTICAL CROP CARE · BANGLADESH'}</p>
    <p>{'কৃষকের জন্য সহজভাবে ফসলের তথ্য।' if is_bn else 'Clear information to help you care for your crops.'}</p>
</div>
""")
