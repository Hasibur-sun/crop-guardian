import json
from pathlib import Path

from diagnosis import diagnose


SUPPORTED_CROPS = {"potato", "tomato", "rice", "brinjal", "jute"}
SUPPORTED_CLASSIFIER_CROPS = {"potato", "tomato"}


def normalize_label(value):
    return str(value or "").lower().replace("_", " ").strip()


def _validation_result(image_path, selected_crop, gemini_result, status, reason):
    """Build a safe early-exit result before loading/running EfficientNet."""
    return {
        "image": image_path.name,
        "selected_crop": selected_crop,
        "efficientnet": None,
        "gemini": gemini_result,
        "crop_agreement": None,
        "disease_agreement": None,
        "global_crop_agreement": None,
        "needs_review": True,
        "status": status,
        "warnings": [reason],
        "image_validation": {
            "is_plant_photo": bool(gemini_result.get("is_plant_photo", False)),
            "detected_crop": gemini_result.get("crop", "unknown"),
            "photo_quality": gemini_result.get("photo_quality", "other"),
            "valid_for_diagnosis": False,
            "reason": reason,
        },
    }


def hybrid_diagnose(image_path: str, selected_crop: str) -> dict:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    selected_crop = normalize_label(selected_crop)
    if selected_crop not in SUPPORTED_CROPS:
        raise ValueError(f"Crop must be one of {sorted(SUPPORTED_CROPS)}")

    print("\nStep 1: Checking the uploaded photograph...")
    try:
        # Gemini validation runs first. EfficientNet is imported lazily below.
        gemini_result = diagnose(str(image_path), use_cache=False)
    except Exception as exc:
        return {
            "image": image_path.name,
            "selected_crop": selected_crop,
            "efficientnet": None,
            "gemini": None,
            "crop_agreement": None,
            "disease_agreement": None,
            "global_crop_agreement": None,
            "needs_review": True,
            "status": "validation_failed",
            "warnings": [f"Image validation failed: {exc}"],
            "image_validation": {
                "is_plant_photo": None,
                "detected_crop": "unknown",
                "photo_quality": "unknown",
                "valid_for_diagnosis": False,
                "reason": "The photograph could not be checked. Please try again.",
            },
        }

    is_plant = bool(gemini_result.get("is_plant_photo", False))
    detected_crop = normalize_label(gemini_result.get("crop", "unknown"))
    photo_quality = normalize_label(gemini_result.get("photo_quality", "other"))

    if not is_plant:
        return _validation_result(
            image_path, selected_crop, gemini_result,
            "invalid_image",
            "This does not appear to be a crop plant photograph. Please upload a clear photo of the crop.",
        )

    if photo_quality != "good":
        quality_messages = {
            "blurry": "The photograph is blurry. Please take a sharper photo of the leaf.",
            "dark": "The photograph is too dark. Please take another photo in good natural light.",
            "too far": "The leaf is too far away. Move closer and photograph the leaf clearly.",
            "other": "The photograph is not suitable for checking. Please upload a clear leaf photo.",
        }
        return _validation_result(
            image_path, selected_crop, gemini_result,
            "poor_image_quality",
            quality_messages.get(photo_quality, "Please upload a clearer photograph of the crop leaf."),
        )

    if detected_crop in {"unknown", "other", ""}:
        return _validation_result(
            image_path, selected_crop, gemini_result,
            "crop_uncertain",
            "The crop type could not be identified confidently. Please check your crop selection and upload a clear leaf photo.",
        )

    if detected_crop != selected_crop:
        return _validation_result(
            image_path, selected_crop, gemini_result,
            "crop_mismatch",
            f"You selected {selected_crop}, but the photograph appears to show {detected_crop}. Please select the correct crop or upload another photo.",
        )

    # The image passed Gemini's plant, quality and selected-crop checks.
    result = {
        "image": image_path.name,
        "selected_crop": selected_crop,
        "efficientnet": None,
        "gemini": gemini_result,
        "crop_agreement": True,
        "disease_agreement": None,
        "global_crop_agreement": None,
        "needs_review": True,
        "status": "gemini_only",
        "warnings": [],
        "image_validation": {
            "is_plant_photo": True,
            "detected_crop": detected_crop,
            "photo_quality": photo_quality,
            "valid_for_diagnosis": True,
            "reason": "The photograph passed the initial image checks.",
        },
    }

    if selected_crop not in SUPPORTED_CLASSIFIER_CROPS:
        result["warnings"].append(
            "EfficientNet does not support this crop. Gemini assessment only; expert review is required."
        )
        return result

    print("Step 2: Running EfficientNet on the validated photograph...")
    try:
        # Lazy import prevents loading PyTorch/model weights for invalid images.
        from classifier import classify
        efficientnet_result = classify(str(image_path), selected_crop=selected_crop)
        result["efficientnet"] = efficientnet_result
    except Exception as exc:
        result["warnings"].append(f"EfficientNet failed: {exc}")
        return result

    gemini_top3 = gemini_result.get("top3", [])
    selected_top3 = efficientnet_result.get("selected_crop_top3", [])
    if not gemini_top3 or not selected_top3:
        result["warnings"].append("One or both models returned no disease candidates.")
        return result

    gemini_top1 = gemini_top3[0]
    efficientnet_top1 = selected_top3[0]
    disease_agreement = (
        normalize_label(efficientnet_top1.get("disease"))
        == normalize_label(gemini_top1.get("disease"))
    )
    global_crop_agreement = bool(
        efficientnet_result.get("selected_crop_matches_global_prediction", False)
    )

    result["disease_agreement"] = disease_agreement
    result["global_crop_agreement"] = global_crop_agreement

    if not global_crop_agreement:
        result["warnings"].append(
            "EfficientNet global crop prediction disagrees with the farmer-selected crop."
        )
    if not disease_agreement:
        result["warnings"].append(
            "EfficientNet and Gemini disagree on the most likely disease."
        )

    if disease_agreement and global_crop_agreement:
        result["status"] = "model_agreement"
        result["needs_review"] = False
    elif disease_agreement:
        result["status"] = "disease_agreement_crop_uncertain"
        result["needs_review"] = True
    else:
        result["status"] = "model_disagreement"
        result["needs_review"] = True

    result["summary"] = {
        "selected_crop": selected_crop,
        "efficientnet_top_prediction": {
            "disease": efficientnet_top1.get("disease"),
            "model_score": efficientnet_top1.get("model_score"),
        },
        "gemini_top_prediction": {
            "disease": gemini_top1.get("disease"),
            "model_score": gemini_top1.get("confidence"),
        },
        "crop_agreement": True,
        "disease_agreement": disease_agreement,
        "global_crop_agreement": global_crop_agreement,
        "status": result["status"],
        "needs_review": result["needs_review"],
    }
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python hybrid_diagnosis.py image_path crop_name")
        raise SystemExit(1)

    output = hybrid_diagnose(sys.argv[1], sys.argv[2])
    print("\n========== HYBRID CROP GUARDIAN ==========")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print("==========================================")
