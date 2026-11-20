# Crop Guardian — Frontend

A premium, farmer-first website for AI-assisted plant health care in Bangladesh.
React + TypeScript + Vite + Tailwind CSS + Lucide icons + React Router. English and Bangla.

It runs **right now in demo mode** (sample data, clearly labelled) and is prepared to connect to your existing
Python backend through a FastAPI layer. The backend is **not** rebuilt or replaced here.

## 1. Install (first time only)

1. Install **Node.js LTS** (version 20 or newer) from https://nodejs.org
2. Open a terminal **inside this folder** (the one containing `package.json`).
3. Run:

```bash
npm install
```

## 2. Start it

```bash
# macOS / Linux
cp .env.example .env
# Windows (Command Prompt)
copy .env.example .env

npm run dev
```

Open the address it prints (normally http://localhost:5173). Phones on the same Wi-Fi can use the "Network" address it prints too.

Other commands: `npm run build` (production build into `dist/`), `npm run preview` (try the build), `npm run typecheck`.

## 3. Demo mode vs live mode

Controlled by `.env`:

| Setting | Meaning |
| --- | --- |
| `VITE_DEMO_MODE=true` | Sample data only. A lime banner says so on every page. Nothing is a real diagnosis, medicine advice or weather. |
| `VITE_DEMO_MODE=false` + `VITE_API_BASE_URL=http://localhost:8000` | Live mode. All requests go to your FastAPI server. |

In demo mode the **Check My Plant** page shows a "Demo outcome" menu so you can preview every result state
(likely identified, needs further checking, unable to identify, healthy). Demo reports are kept in the browser's local storage only.
The only medicine card in demo mode is clearly marked "Sample layout only. Not a real product."

## 4. Adding real photography

The site shows original botanical artwork until you add photos. Put JPG files in `public/images/` using the names listed in
`public/images/README.md` (for example `hero.jpg`, `crop-tomato.jpg`). They replace the artwork automatically. Use only photos you own or are licensed to use.

## 5. Project structure

```
crop-guardian/
├─ .env.example               environment template
├─ docs/BACKEND_INTEGRATION.md   endpoint contract + FastAPI skeleton
├─ public/                    favicon, images/ (photo slots)
└─ src/
   ├─ main.tsx, App.tsx, index.css
   ├─ types/api.ts            TypeScript interfaces for every API response
   ├─ lib/
   │  ├─ api/index.ts         picks demo or live client (the only thing pages import)
   │  ├─ api/client.ts        live client (fetch to VITE_API_BASE_URL)
   │  ├─ api/demo.ts          demo client (sample data, flagged isDemo)
   │  ├─ diseaseData.ts       demo guide text for the 13 classes, English + Bangla
   │  ├─ config.ts, crops.ts, field.ts, format.ts
   ├─ i18n/                  en.ts, bn.ts, provider (language switch, saved on device)
   ├─ hooks/useAsync.ts
   ├─ components/            Navbar, Footer, Button, Photo, Art, Reveal, StatusBadge, Lists, ...
   └─ pages/                 Home, CheckPlant, Results, Guide, GuideDetail, Weather, History, About, NotFound
```

## 6. Design notes

- Palette and fonts follow the brief (DM Serif Display + Manrope; Noto Sans/Serif Bengali for Bangla). Fonts load from Google Fonts.
- Disease names stay in English in both languages on purpose. All other text is translated.
- The UI never shows model names, scores, confidence percentages or coordinates in farmer-facing screens. Raw JSON is behind a collapsed "Technical details" section.
- Medicine information appears only when the backend marks it `verified`; otherwise the "no verified medicine instructions" message is shown.
- Animations are restrained and switch off for users who prefer reduced motion.

See `docs/BACKEND_INTEGRATION.md` to connect the real backend.
