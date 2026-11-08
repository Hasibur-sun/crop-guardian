
import json
from pathlib import Path

from classifier import classify
from diagnosis import diagnose


# ==========================================
# 1. CONFIGURATION
# ==========================================

SUPPORTED_CLASSIFIER_CROPS = {
    "potato",
    "tomato"
}


# ==========================================
# 2. NORMALIZE LABELS
# ==========================================

def normalize_label(value):
    """Normalize disease names for comparison."""

    return (
        str(value)
        .lower()
        .replace("_", " ")
        .strip()
    )


# ==========================================
# 3. HYBRID DIAGNOSIS
# ==========================================

def hybrid_diagnose(
    image_path: str,
    selected_crop: str
) -> dict:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    selected_crop = selected_crop.lower().strip()

    valid_crops = {
        "potato", "tomato", "rice",
        "brinjal", "jute"
    }

    if selected_crop not in valid_crops:
        raise ValueError(
            f"Crop must be one of {sorted(valid_crops)}"
        )

    result = {
        "image": image_path.name,
        "selected_crop": selected_crop,
        "efficientnet": None,
        "gemini": None,
        "crop_agreement": None,
        "disease_agreement": None,
        "needs_review": True,
        "status": "uncertain",
        "warnings": []
    }

    # ======================================
    # 4. RUN EFFICIENTNET
    # ======================================

    if selected_crop in SUPPORTED_CLASSIFIER_CROPS:

        try:
            efficientnet_result = classify(
                str(image_path),
                selected_crop=selected_crop
            )

            result["efficientnet"] = efficientnet_result

        except Exception as e:

            result["warnings"].append(
                f"EfficientNet failed: {str(e)}"
            )

    else:

        result["warnings"].append(
            "EfficientNet does not support this crop. "
            "Using Gemini only."
        )

    # ======================================
    # 5. RUN GEMINI
    # ======================================

    try:

        gemini_result = diagnose(str(image_path))

        result["gemini"] = gemini_result

    except Exception as e:

        result["warnings"].append(
            f"Gemini diagnosis failed: {str(e)}"
        )

        return result

    # ======================================
    # 6. GEMINI CROP CHECK
    # ======================================

    gemini_crop = str(
        gemini_result.get("crop", "unknown")
    ).lower()

    crop_agreement = (
        gemini_crop == selected_crop
    )

    result["crop_agreement"] = crop_agreement

    if not crop_agreement:

        result["warnings"].append(
            "Gemini crop prediction disagrees "
            "with the farmer-selected crop."
        )

    # ======================================
    # 7. GEMINI DISEASE PREDICTION
    # ======================================

    gemini_top3 = gemini_result.get("top3", [])

    gemini_top1 = (
        gemini_top3[0]
        if gemini_top3
        else None
    )

    if gemini_top1 is None:

        result["warnings"].append(
            "Gemini returned no disease candidates."
        )

        return result

    gemini_disease = normalize_label(
        gemini_top1["disease"]
    )

    # ======================================
    # 8. COMPARE EFFICIENTNET AND GEMINI
    # ======================================

    efficientnet_result = result["efficientnet"]

    if efficientnet_result is None:

        result["status"] = "gemini_only"
        result["needs_review"] = True

        result["warnings"].append(
            "No independent EfficientNet prediction "
            "is available for comparison."
        )

        return result

    selected_top3 = efficientnet_result.get(
        "selected_crop_top3", []
    )

    if not selected_top3:

        result["warnings"].append(
            "EfficientNet returned no crop-specific candidates."
        )

        return result

    efficientnet_top1 = selected_top3[0]

    efficientnet_disease = normalize_label(
        efficientnet_top1["disease"]
    )

    disease_agreement = (
        efficientnet_disease == gemini_disease
    )

    result["disease_agreement"] = disease_agreement

    # ======================================
    # 9. FINAL RELIABILITY CHECK
    # ======================================

    global_crop_agreement = (
        efficientnet_result.get(
            "selected_crop_matches_global_prediction",
            False
        )
    )

    if not global_crop_agreement:

        result["warnings"].append(
            "EfficientNet global crop prediction "
            "disagrees with farmer-selected crop."
        )

    if not disease_agreement:

        result["warnings"].append(
            "EfficientNet and Gemini disagree "
            "on the most likely disease."
        )

    # Do not automatically choose either model
    if (
        crop_agreement
        and disease_agreement
        and global_crop_agreement
    ):

        result["status"] = "model_agreement"
        result["needs_review"] = False

    else:

        result["status"] = "model_disagreement"
        result["needs_review"] = True

    # ======================================
    # 10. FINAL RESPONSE
    # ======================================

    result["summary"] = {
        "selected_crop": selected_crop,

        "efficientnet_top_prediction": {
            "disease": efficientnet_top1["disease"],
            "model_score": efficientnet_top1["model_score"]
        },

        "gemini_top_prediction": {
            "disease": gemini_top1["disease"],
            "model_score": gemini_top1["confidence"]
        },

        "crop_agreement": crop_agreement,
        "disease_agreement": disease_agreement,

        "recommendation": (
            "Show both assessments and request "
            "agriculture officer confirmation."
            if result["needs_review"]
            else "Show the matching assessments, "
                 "but do not treat model agreement as proof."
        )
    }

    return result


# ==========================================
# 11. TERMINAL TEST
# ==========================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 3:

        print(
            "Usage: python hybrid_diagnosis.py "
            "image_path crop_name"
        )

        raise SystemExit(1)

    image_path = sys.argv[1]
    crop_name = sys.argv[2]

    output = hybrid_diagnose(
        image_path,
        crop_name
    )

    print("\n========== HYBRID CROP GUARDIAN ==========")

    print(json.dumps(
        output,
        indent=2,
        ensure_ascii=False
    ))

    print("==========================================")
