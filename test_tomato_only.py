
import torch
import json
import sys
import timm

from pathlib import Path
from PIL import Image
from torchvision import transforms as T

BASE = Path(__file__).resolve().parent

CLASSES = json.load(
    open(BASE / "models/classes.json", encoding="utf-8")
)

DEVICE = torch.device("cpu")

model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=len(CLASSES)
)

state = torch.load(
    BASE / "models/crop_classifier.pt",
    map_location=DEVICE,
    weights_only=True
)

model.load_state_dict(state)
model.eval()

transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(
        (0.485, 0.456, 0.406),
        (0.229, 0.224, 0.225)
    )
])

image_path = BASE / (
    sys.argv[1] if len(sys.argv) > 1
    else "test_images/tomato_early_blight_1.jpg"
)

with Image.open(image_path) as img:
    x = transform(img.convert("RGB")).unsqueeze(0)

with torch.inference_mode():
    probabilities = torch.softmax(model(x), dim=1)[0]

# Restrict predictions to tomato classes
indices = [
    i for i, name in enumerate(CLASSES)
    if name.startswith("Tomato___")
]

indices.sort(
    key=lambda i: probabilities[i].item(),
    reverse=True
)

print("\nTOMATO-ONLY PREDICTIONS")

for i in indices[:5]:
    print(
        CLASSES[i],
        round(probabilities[i].item(), 4)
    )
