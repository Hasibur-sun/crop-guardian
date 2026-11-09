
import torch
import json
from pathlib import Path
from PIL import Image
from torchvision import transforms as T
import timm

BASE = Path(__file__).resolve().parent

with open(BASE / "models/classes.json", encoding="utf-8") as f:
    classes = json.load(f)

device = torch.device("cpu")

model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=len(classes)
)

state = torch.load(
    BASE / "models/crop_classifier.pt",
    map_location=device,
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

image_path = BASE / "test_images/potato_late_blight_1.jpg"

with Image.open(image_path) as img:
    x = transform(img.convert("RGB")).unsqueeze(0)

with torch.inference_mode():
    probabilities = torch.softmax(model(x), dim=1)[0]

# Show all potato classes only
print("\nPOTATO-ONLY PREDICTIONS")

potato_indices = [
    i for i, name in enumerate(classes)
    if name.startswith("Potato___")
]

for i in sorted(
    potato_indices,
    key=lambda idx: probabilities[idx].item(),
    reverse=True
):
    print(
        classes[i],
        round(probabilities[i].item(), 4)
    )
