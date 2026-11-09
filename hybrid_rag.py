
import json
from pathlib import Path

from hybrid_diagnosis import hybrid_diagnose
from rag import search as search_knowledge


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_FILE = (
    BASE_DIR / "knowledge" / "disease_knowledge.json"
)

SUPPORTED_CROPS = {
    "potato",
    "tomato",
    "rice",
    "brinjal",
    "jute"
}


# ==========================================
# 2. NORMALIZE DISEASE NAMES
# ==========================================

def normalize_name(value):

    return (
        str(value)
        .lower()
        .replace("_", " ")
        .strip()
    )


# ==========================================
# 3. LOAD KNOWLEDGE ENTRIES
# ==========================================

def load_knowledge():

    with open(
        KNOWLEDGE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================================
# 4. COLLECT MODEL PREDICTIONS
# ==========================================

def collect_predictions(hybrid_result, selected_crop):

    candidates = []

    # --------------------------------------
    # EfficientNet prediction
    # --------------------------------------

    efficientnet = hybrid_result.get("efficientnet")

    if efficientnet:

        predictions = efficientnet.get(
            "selected_crop_top3", []
        )

        if predictions:

            top = predictions[0]

            candidates.append({
                "source_model": "EfficientNet-B0",
                "crop": selected_crop,
                "disease": top["disease"],
                "model_score": top["model_score"]
            })

    # --------------------------------------
    # Gemini prediction
    # --------------------------------------

    gemini = hybrid_result.get("gemini")

    if gemini:

        predictions = gemini.get("top3", [])

        if predictions:

            top = predictions[0]

            candidates.append({
                "source_model": "Gemini",
                "crop": gemini.get("crop", "unknown"),
                "disease": top["disease"],
                "model_score": top["confidence"]
            })

    return candidates


# ==========================================
# 5. HYBRID + RAG DIAGNOSIS
# ==========================================

def diagnose_with_knowledge(
    image_path: str,
    selected_crop: str
):

    selected_crop = selected_crop.lower().strip()

    if selected_crop not in SUPPORTED_CROPS:

        raise ValueError(
            f"Unsupported crop: {selected_crop}"
        )

    # --------------------------------------
    # A. Run existing hybrid diagnosis
    # --------------------------------------

    print("\nRunning hybrid diagnosis...")

    hybrid_result = hybrid_diagnose(
        image_path,
        selected_crop
    )

    # --------------------------------------
    # B. Collect model predictions
    # --------------------------------------

    candidates = collect_predictions(
        hybrid_result,
        selected_crop
    )

    result = {

        "image": Path(image_path).name,

        "selected_crop": selected_crop,

        "hybrid_status": hybrid_result.get(
            "status", "uncertain"
        ),

        "crop_agreement": hybrid_result.get(
            "crop_agreement"
        ),

        "disease_agreement": hybrid_result.get(
            "disease_agreement"
        ),

        "needs_review": hybrid_result.get(
            "needs_review", True
        ),

        "model_predictions": candidates,

        "knowledge_retrieval": [],

        "farmer_guidance_allowed": False,

        "final_message": "",

        "warnings": list(
            hybrid_result.get("warnings", [])
        )
    }

    if not candidates:

        result["final_message"] = (
            "No reliable disease prediction is available. "
            "Please upload a clearer photograph or seek "
            "advice from an agriculture officer."
        )

        return result

    # --------------------------------------
    # C. Retrieve knowledge for predictions
    # --------------------------------------

    print("\nSearching agricultural knowledge base...")

    retrieved = {}

    for candidate in candidates:

        crop = candidate["crop"].lower().strip()

        disease = candidate["disease"]

        # Skip invalid crop predictions
        if crop != selected_crop:

            result["warnings"].append(
                f"{candidate['source_model']} predicted "
                f"{crop}, which differs from selected crop "
                f"{selected_crop}."
            )

            continue

        # Skip Healthy and Unknown
        if normalize_name(disease) in {
            "healthy",
            "unknown"
        }:

            result["warnings"].append(
                f"No disease knowledge search performed "
                f"for prediction: {disease}"
            )

            continue

        key = (
            crop,
            normalize_name(disease)
        )

        # Avoid duplicate database searches
        if key not in retrieved:

            retrieval = search_knowledge(
                crop=crop,
                disease=disease
            )

            retrieved[key] = retrieval

        else:

            retrieval = retrieved[key]

        result["knowledge_retrieval"].append({

            "predicted_by": candidate["source_model"],

            "predicted_disease": disease,

            "model_score": candidate["model_score"],

            "retrieval_status": retrieval["status"],

            "knowledge": retrieval.get(
                "matches", []
            )

        })

    # --------------------------------------
    # D. Check knowledge verification
    # --------------------------------------

    
    # ======================================
    # D. CHECK KNOWLEDGE AND HEALTHY STATUS
    # ======================================

    knowledge_matches = []

    for retrieval in result["knowledge_retrieval"]:
        knowledge_matches.extend(
            retrieval["knowledge"]
        )

    # Check whether every model predicted Healthy or Unknown
    all_healthy_or_unknown = all(
        normalize_name(item["disease"]) in {
            "healthy",
            "unknown"
        }
        for item in candidates
    )

    # --------------------------------------
    # E. HANDLE HEALTHY / UNKNOWN PREDICTIONS
    # --------------------------------------

    if all_healthy_or_unknown:

        result["farmer_guidance_allowed"] = False

        result["final_message"] = (
            "Both models predicted that the plant is healthy. "
            "However, the EfficientNet global crop prediction "
            "disagrees with the selected crop. The result is "
            "not independently confirmed. No disease-specific "
            "knowledge search was performed. Please seek "
            "agriculture officer confirmation if symptoms are present."
        )

        result["needs_review"] = True

        return result

    # --------------------------------------
    # F. HANDLE MISSING KNOWLEDGE
    # --------------------------------------

    if not knowledge_matches:

        result["farmer_guidance_allowed"] = False

        result["final_message"] = (
            "No matching agricultural knowledge was found. "
            "Do not provide treatment recommendations."
        )

        return result

    # --------------------------------------
    # G. CHECK SOURCE VERIFICATION
    # --------------------------------------

    all_verified = all(
        match["verification_status"] == "verified"
        for match in knowledge_matches
    )

    models_agree = (
        hybrid_result.get("status") == "model_agreement"
        and not hybrid_result.get("needs_review", True)
    )

    result["farmer_guidance_allowed"] = (
        all_verified and models_agree
    )

    # --------------------------------------
    # H. FINAL DECISION
    # --------------------------------------

    if not models_agree:

        result["final_message"] = (
            "The AI models disagree or require review. "
            "Both predictions and their source references "
            "are available for examination. Please seek "
            "confirmation from an agriculture officer."
        )

        result["needs_review"] = True

    elif not all_verified:

        result["final_message"] = (
            "Matching agricultural information was retrieved, "
            "but its recommendations have not passed final "
            "source verification. Do not present them as "
            "approved treatment advice."
        )

        result["needs_review"] = True

    else:

        result["final_message"] = (
            "The models agree and verified agricultural "
            "knowledge was retrieved. Present supported "
            "recommendations with source references."
        )

    return result

# ==========================================
# 6. TERMINAL TEST
# ==========================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print(
            "Usage: python hybrid_rag.py "
            "image_path crop_name"
        )

        raise SystemExit(1)

    image_path = sys.argv[1]

    selected_crop = sys.argv[2]

    output = diagnose_with_knowledge(
        image_path,
        selected_crop
    )

    print(
        "\n========== CROP GUARDIAN HYBRID RAG =========="
    )

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False
        )
    )

    print(
        "\n=============================================="
    )
