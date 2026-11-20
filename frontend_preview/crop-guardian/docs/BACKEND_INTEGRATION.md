# Backend integration

The frontend talks to your existing Python project only through a thin **FastAPI** layer.
Do not rebuild the classifier, Gemini assessment, hybrid engine, RAG, NASA POWER, history or PDF code:
wrap what exists. Endpoints below do **not** exist yet; the frontend is written against this contract
(`src/types/api.ts` holds the TypeScript versions).

## Turning it on

1. Start FastAPI (for example `uvicorn app:app --port 8000`) with CORS allowing `http://localhost:5173`.
2. In `.env`: `VITE_API_BASE_URL=http://localhost:8000` and `VITE_DEMO_MODE=false`.
3. Restart `npm run dev`.

## Endpoints

| Method | Path | Request | Response |
| --- | --- | --- | --- |
| POST | `/api/diagnose` | multipart: `image`, `crop`, `lang`, optional `latitude`, `longitude` | `DiagnosisReport` |
| GET | `/api/weather` | `latitude`, `longitude`, optional `crop`, `lang` | `WeatherReport` |
| POST | `/api/weather/update` | JSON `FieldLocation` | `FieldLocation` |
| GET | `/api/history` | optional `crop`, `q`, `lang` | `HistoryItem[]` |
| GET | `/api/history/{id}` | optional `lang` | `DiagnosisReport` |
| GET | `/api/history/{id}/pdf` | | `application/pdf` |
| GET | `/api/diseases` | optional `crop`, `q`, `lang` | `DiseaseSummary[]` |
| GET | `/api/diseases/{id}` | optional `lang` | `DiseaseDetail` |

`crop` is one of `potato, tomato, rice, brinjal, jute`. `lang` is `en` or `bn`.

## DiagnosisReport (shape)

```json
{
  "id": "20261118-0001",
  "createdAt": "2026-11-18T12:00:00Z",
  "lang": "en",
  "crop": "tomato",
  "status": "likely_identified",
  "disease": { "id": "tomato-early-blight", "name": "Early Blight", "isHealthy": false },
  "summary": "Plain-language explanation.",
  "symptoms": ["..."],
  "causes": ["..."],
  "actions": ["..."],
  "treatment": { "verified": true, "products": [ { "name": "", "activeIngredient": "", "manufacturer": "",
    "registeredCrop": "", "registeredDisease": "", "labelDosage": "", "applicationInstructions": "",
    "safetyPrecautions": [""], "preHarvestInterval": "" } ] },
  "prevention": ["..."],
  "weather": { "summary": "...", "points": ["..."] },
  "imageUrl": "https://.../photo.jpg",
  "technical": { "anything": "raw JSON for the optional Technical Details section" }
}
```

Rules the UI relies on:

- `status` is `likely_identified`, `needs_checking` or `unable_to_identify`. Set it only when the hybrid engine supports it.
- `treatment.verified` must be `true` **only** for label-verified products. Otherwise send `{ "verified": false, "products": [] }` and the UI shows the "no verified medicine" message. Never send guessed products or doses.
- `causes` should be empty when the RAG source has nothing; the section is then hidden.
- Put EfficientNet / Gemini / scores / coordinates inside `technical` only. Farmer-facing fields must stay plain language.
- Return text already in the requested `lang`. Keep disease `name` in English.
- For healthy leaves send `disease.isHealthy: true`; the UI then shows care guidance and no medicine section.
- Weather text must describe conditions only and never claim it confirms a disease.

## WeatherReport (shape)

```json
{
  "location": { "label": "Tangail", "latitude": 24.25, "longitude": 89.92 },
  "observation": { "temperatureC": 29.4, "humidityPct": 83, "rainfallMm": 23.1,
                   "periodLabel": "Last 7 days", "observedAt": "2026-11-18T00:00:00Z" },
  "daily": [ { "date": "2026-11-17", "temperatureC": 29, "humidityPct": 85, "rainfallMm": 3.2 } ],
  "cropContext": ["Everyday-language crop-specific message"],
  "guidance": ["Everyday-language tip"],
  "source": "NASA POWER"
}
```

## FastAPI skeleton

Replace the `your_project` imports with your real functions; the route shapes are what matters.

```python
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
                   allow_methods=["*"], allow_headers=["*"])

@app.post("/api/diagnose")
async def diagnose(image: UploadFile = File(...), crop: str = Form(...), lang: str = Form("en"),
                   latitude: float | None = Form(None), longitude: float | None = Form(None)):
    # 1. save the upload  2. run your hybrid diagnosis engine  3. fetch RAG knowledge + NASA POWER weather
    # 4. save to history  5. return the DiagnosisReport shape above
    ...

@app.get("/api/history/{report_id}/pdf")
def pdf(report_id: str):
    return FileResponse(your_pdf_path_for(report_id), media_type="application/pdf")
```
