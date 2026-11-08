
import json
import torch
import timm

from pathlib import Path
from PIL import Image, ImageOps
from torchvision import transforms as T


# =====================================
# 1. CONFIGURATION
# =====================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "crop_classifier.pt"
CLASSES_PATH = MODEL_DIR / "classes.json"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

SUPPORTED_CROPS = ["potato", "tomato"]


# =====================================
# 2. LOAD CLASSES
# =====================================

with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    CLASSES = json.load(f)


# =====================================
# 3. LOAD MODEL
# =====================================

model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=len(CLASSES)
)

state_dict = torch.load(
    MODEL_PATH,
    map_location=DEVICE,
    weights_only=True
)

model.load_state_dict(state_dict)
model.to(DEVICE)
model.eval()


# =====================================
# 4. IMAGE TRANSFORMATION
# =====================================

transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(
        (0.485, 0.456, 0.406),
        (0.229, 0.224, 0.225)
    )
])


# =====================================
# 5. CLASSIFICATION
# =====================================

def classify(path: str, selected_crop: str = None) -> dict:

    image_path = Path(path)

    if not image_path.exists():
        raise FileNotFoundError(image_path)

    if selected_crop is not None:
        selected_crop = selected_crop.lower().strip()

        if selected_crop not in SUPPORTED_CROPS:
            raise ValueError(
                f"Supported crops: {SUPPORTED_CROPS}"
            )

    # Prepare image
    with Image.open(image_path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        image = transform(img).unsqueeze(0)

    image = image.to(DEVICE)

    # Run model
    with torch.inference_mode():
        outputs = model(image)
        probabilities = torch.softmax(outputs, dim=1)[0]

    # Global top 3
    global_top = probabilities.topk(
        min(3, len(CLASSES))
    )

    global_predictions = []

    for score, index in zip(
        global_top.values,
        global_top.indices
    ):
        crop_name, disease = CLASSES[index.item()].split("___", 1)

        global_predictions.append({
            "crop": crop_name.lower(),
            "disease": disease,
            "model_score": round(score.item(), 4)
        })

    global_crop = global_predictions[0]["crop"]

    result = {
        "model": "EfficientNet-B0",
        "device": str(DEVICE),
        "selected_crop": selected_crop,
        "global_top3": global_predictions,
        "global_top_crop": global_crop
    }

    # No crop selected: return global predictions
    if selected_crop is None:
        result["needs_review"] = True
        result["reason"] = "Crop selection is required for crop-specific diagnosis."
        return result

    # Filter classes to selected crop
    crop_indices = [
        i for i, name in enumerate(CLASSES)
        if name.split("___", 1)[0].lower() == selected_crop
    ]

    if not crop_indices:
        raise ValueError(
            f"No model classes found for {selected_crop}"
        )

    crop_scores = probabilities[crop_indices]

    order = torch.argsort(
        crop_scores,
        descending=True
    )[:3]

    selected_predictions = []

    for position in order:
        index = crop_indices[position.item()]
        crop_name, disease = CLASSES[index].split("___", 1)

        selected_predictions.append({
            "crop": crop_name.lower(),
            "disease": disease,
            "model_score": round(
                probabilities[index].item(), 4
            )
        })

    # Detect crop disagreement
    crop_matches = global_crop == selected_crop

    result["selected_crop_top3"] = selected_predictions
    result["selected_crop_matches_global_prediction"] = crop_matches

    result["selected_crop_probability_mass"] = round(
        crop_scores.sum().item(), 4
    )

    result["needs_review"] = not crop_matches

    if not crop_matches:
        result["reason"] = (
            "The model's global top prediction disagrees "
            "with the farmer-selected crop."
        )
    else:
        result["reason"] = (
            "Crop selection and global prediction agree. "
            "Disease scores still require reliability assessment."
        )

    return result


# =====================================
# 6. TERMINAL TEST
# =====================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python classifier.py image_path [potato|tomato]"
        )
        raise SystemExit(1)

    image_path = sys.argv[1]

    selected_crop = (
        sys.argv[2] if len(sys.argv) >= 3 else None
    )

    result = classify(
        image_path,
        selected_crop
    )

    print("\n========== CROP GUARDIAN ==========")

    print(json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ))

    print("===================================")
