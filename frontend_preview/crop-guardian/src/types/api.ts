/**
 * Shared TypeScript contracts between the frontend and the FastAPI integration layer.
 * See docs/BACKEND_INTEGRATION.md for the matching JSON examples.
 *
 * Farmer-facing screens never show model names, scores or percentages. Anything technical
 * belongs in `DiagnosisReport.technical`, which is only shown inside an optional collapsed section.
 */

export type Lang = 'en' | 'bn'
export type CropId = 'potato' | 'tomato' | 'rice' | 'brinjal' | 'jute'

/** Only use these when the backend assessment supports them. */
export type DiagnosisStatus = 'likely_identified' | 'needs_checking' | 'unable_to_identify'

export interface DiseaseRef {
  id: string
  /** Disease names stay in English in both languages on purpose. */
  name: string
  isHealthy: boolean
}

/** Verified product information. Never fill this from a guess. */
export interface Medicine {
  name: string
  activeIngredient: string
  manufacturer: string
  registeredCrop: string
  registeredDisease: string
  labelDosage: string
  applicationInstructions: string
  safetyPrecautions: string[]
  preHarvestInterval: string
  /** True only in demo mode: marks a layout sample that is not a real product. */
  sample?: boolean
}

export interface TreatmentInfo {
  /** True only when the backend has verified label data for this crop + disease. */
  verified: boolean
  products: Medicine[]
}

export interface FieldLocation {
  label?: string
  latitude: number
  longitude: number
}


export interface WeatherObservation {
  temperatureC: number | null
  humidityPct: number | null
  rainfallMm: number | null
  periodLabel: string
  observedAt: string | null
  isFresh: boolean
  freshnessMessage: string
}

export interface DailyWeather {
  date: string
  temperatureC: number | null
  humidityPct: number | null
  rainfallMm: number | null
}

export interface WeatherReport {
  location: FieldLocation
  observation: WeatherObservation
  daily: DailyWeather[]
  cropContext: string[]
  guidance: string[]
  source: string
  isDemo?: boolean
}


export interface ReportWeather {
  summary: string
  points: string[]
  isDemo?: boolean
}

export interface DiagnosisReport {
  id: string
  createdAt: string
  lang: Lang
  crop: CropId
  status: DiagnosisStatus
  disease: DiseaseRef | null
  /** One or two plain sentences explaining the problem. */
  summary: string
  symptoms: string[]
  causes: string[]
  actions: string[]
  treatment: TreatmentInfo
  prevention: string[]
  weather: ReportWeather | null
  imageUrl?: string
  /** Hidden by default. Raw backend JSON for advisors and developers. */
  technical: Record<string, unknown>
  isDemo?: boolean
}

export interface HistoryItem {
  id: string
  createdAt: string
  crop: CropId
  status: DiagnosisStatus
  diseaseName: string | null
  isHealthy: boolean
  thumbUrl?: string
  isDemo?: boolean
}

export interface DiseaseSummary {
  id: string
  crop: CropId
  name: string
  isHealthy: boolean
  blurb: string
}

export interface DiseaseDetail extends DiseaseSummary {
  overview: string
  symptoms: string[]
  causes: string[]
  prevention: string[]
  management: string[]
  treatment: TreatmentInfo
}

/** Demo-only switch so every result state can be previewed. Ignored by the live API. */
export type DemoScenario = 'auto' | 'likely' | 'check' | 'unable' | 'healthy'

export interface DiagnoseInput {
  image: File
  crop: CropId
  lang: Lang
  location?: FieldLocation
  scenario?: DemoScenario
}

export interface WeatherQuery {
  latitude: number
  longitude: number
  crop?: CropId
  lang: Lang
}

export interface HistoryQuery {
  crop?: CropId
  q?: string
  lang: Lang
}

export interface DiseaseQuery {
  crop?: CropId
  q?: string
  lang: Lang
}

export interface CropGuardianApi {
  /** POST /api/diagnose (multipart: image, crop, lang, latitude?, longitude?) */
  diagnose(input: DiagnoseInput, signal?: AbortSignal): Promise<DiagnosisReport>
  /** GET /api/weather */
  getWeather(q: WeatherQuery): Promise<WeatherReport>
  /** POST /api/weather/update */
  updateFieldLocation(loc: FieldLocation): Promise<FieldLocation>
  /** GET /api/history */
  listHistory(q: HistoryQuery): Promise<HistoryItem[]>
  /** GET /api/history/{id} */
  getReport(id: string, lang: Lang): Promise<DiagnosisReport>
  /** GET /api/history/{id}/pdf — returns 'print' when the browser print dialog should be used instead. */
  downloadReportPdf(id: string): Promise<'downloaded' | 'print'>
  /** GET /api/diseases */
  listDiseases(q: DiseaseQuery): Promise<DiseaseSummary[]>
  /** GET /api/diseases/{id} */
  getDisease(id: string, lang: Lang): Promise<DiseaseDetail>
}
