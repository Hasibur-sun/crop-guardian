import type {
  CropGuardianApi,
  CropId,
  DemoScenario,
  DiagnosisReport,
  DiagnosisStatus,
  HistoryItem,
  Lang,
  Medicine,
  WeatherReport,
} from '../../types/api'
import { cropHealthyId, detail, summaries } from '../diseaseData'

/**
 * DEMO MODE API.
 * Everything returned here is sample data so the interface can be previewed before the backend is connected.
 * It is always flagged `isDemo: true`, and the UI labels it. It is never a real diagnosis, real medicine
 * advice or real weather.
 */

const HISTORY_KEY = 'cg.demo.history'
const MAX_ITEMS = 30

interface Stored {
  id: string
  createdAt: string
  crop: CropId
  status: DiagnosisStatus
  diseaseId: string | null
  imageUrl?: string
  scenario: DemoScenario
}

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms)
    signal?.addEventListener('abort', () => {
      clearTimeout(t)
      reject(new DOMException('Aborted', 'AbortError'))
    })
  })

function readAll(): Stored[] {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? '[]') as Stored[]
  } catch {
    return []
  }
}

function writeAll(items: Stored[]) {
  const trimmed = items.slice(0, MAX_ITEMS)
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed))
  } catch {
    // Storage full: keep the newest few without photos.
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed.slice(0, 8).map((s) => ({ ...s, imageUrl: undefined }))))
    } catch {
      /* ignore */
    }
  }
}

/** Shrink the photo so it fits comfortably in browser storage. */
function resizeImage(file: File, maxSide = 640): Promise<string | undefined> {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      const scale = Math.min(1, maxSide / Math.max(img.width, img.height))
      const canvas = document.createElement('canvas')
      canvas.width = Math.round(img.width * scale)
      canvas.height = Math.round(img.height * scale)
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        URL.revokeObjectURL(url)
        return resolve(undefined)
      }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
      URL.revokeObjectURL(url)
      resolve(canvas.toDataURL('image/jpeg', 0.7))
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(undefined)
    }
    img.src = url
  })
}

// ---- scenario logic -------------------------------------------------------

function chooseOutcome(crop: CropId, scenario: DemoScenario): { status: DiagnosisStatus; diseaseId: string | null } {
  const supported = crop === 'potato' || crop === 'tomato'
  if (!supported || scenario === 'unable') return { status: 'unable_to_identify', diseaseId: null }
  const lateBlight = `${crop}-late-blight`
  const earlyBlight = `${crop}-early-blight`
  switch (scenario) {
    case 'healthy':
      return { status: 'likely_identified', diseaseId: cropHealthyId(crop) }
    case 'check':
      return { status: 'needs_checking', diseaseId: lateBlight }
    case 'likely':
      return { status: 'likely_identified', diseaseId: earlyBlight }
    default:
      return crop === 'tomato'
        ? { status: 'likely_identified', diseaseId: earlyBlight }
        : { status: 'needs_checking', diseaseId: lateBlight }
  }
}

const T = {
  summaryLikely: {
    en: 'The visible symptoms on this leaf match this problem.',
    bn: 'এই পাতার দৃশ্যমান লক্ষণ এই সমস্যার সাথে মিলছে।',
  },
  summaryCheck: {
    en: 'Some symptoms match this problem, but the photo is not clear enough to be sure. Please check the plant in person.',
    bn: 'কিছু লক্ষণ এই সমস্যার সাথে মিলছে, তবে ছবি থেকে নিশ্চিত হওয়া যাচ্ছে না। গাছটি সরাসরি দেখে নিশ্চিত হোন।',
  },
  summaryUnable: {
    en: 'We could not match the leaf in this photo to a problem we know. This does not mean the plant is healthy.',
    bn: 'এই ছবির পাতাটি আমাদের জানা কোনো সমস্যার সাথে মেলানো যায়নি। এর মানে এই নয় যে গাছটি সুস্থ।',
  },
  unableActions: [
    {
      en: 'Take a new photo in daylight, close to one affected leaf, with the leaf filling most of the picture.',
      bn: 'দিনের আলোতে একটি আক্রান্ত পাতার কাছ থেকে নতুন ছবি তুলুন, যাতে পাতাটি ছবির বেশিরভাগ জায়গা জুড়ে থাকে।',
    },
    {
      en: 'Check that you selected the right crop.',
      bn: 'সঠিক ফসল বেছে নিয়েছেন কিনা দেখুন।',
    },
    {
      en: 'Show the plant to a local agricultural officer.',
      bn: 'গাছটি স্থানীয় কৃষি কর্মকর্তাকে দেখান।',
    },
  ],
  checkActions: [
    {
      en: 'Look at several leaves in daylight and compare them with the symptoms above.',
      bn: 'দিনের আলোতে কয়েকটি পাতা দেখুন এবং উপরের লক্ষণের সাথে মিলিয়ে নিন।',
    },
    {
      en: 'Show the plant to a local agricultural officer to confirm.',
      bn: 'নিশ্চিত হতে গাছটি স্থানীয় কৃষি কর্মকর্তাকে দেখান।',
    },
  ],
  weatherSummary: {
    en: 'Sample weather: warm, humid days with some rain. Weather does not confirm a disease, but humid and wet periods can help some leaf problems spread.',
    bn: 'নমুনা আবহাওয়া: উষ্ণ ও আর্দ্র দিন, সঙ্গে কিছু বৃষ্টি। আবহাওয়া দিয়ে রোগ নিশ্চিত করা যায় না, তবে আর্দ্র ও ভেজা সময়ে কিছু পাতার রোগ সহজে ছড়াতে পারে।',
  },
  weatherPoints: [
    {
      en: 'Leaves that stay wet for a long time make it easier for many leaf diseases to spread.',
      bn: 'পাতা দীর্ঘ সময় ভেজা থাকলে অনেক পাতার রোগ সহজে ছড়ায়।',
    },
    {
      en: 'Check the underside of leaves on damp mornings.',
      bn: 'ভেজা সকালে পাতার নিচের দিকটা দেখুন।',
    },
  ],
}

function sampleMedicine(lang: Lang, crop: CropId, disease: string): Medicine {
  const tx = (en: string, bn: string) => (lang === 'bn' ? bn : en)
  return {
    sample: true,
    name: tx('Sample Product Name', 'নমুনা পণ্যের নাম'),
    activeIngredient: tx('Sample active ingredient', 'নমুনা সক্রিয় উপাদান'),
    manufacturer: tx('Sample manufacturer', 'নমুনা প্রস্তুতকারক'),
    registeredCrop: crop,
    registeredDisease: disease,
    labelDosage: tx('Dosage from the official label appears here.', 'এখানে অফিসিয়াল লেবেলের মাত্রা দেখানো হবে।'),
    applicationInstructions: tx(
      'Application instructions from the official label appear here.',
      'এখানে অফিসিয়াল লেবেল অনুযায়ী ব্যবহারের নিয়ম দেখানো হবে।',
    ),
    safetyPrecautions: [
      tx('Safety precautions from the official label appear here.', 'এখানে অফিসিয়াল লেবেলের নিরাপত্তা সতর্কতা দেখানো হবে।'),
    ],
    preHarvestInterval: tx('From the official label', 'অফিসিয়াল লেবেল অনুযায়ী'),
  }
}

function buildReport(s: Stored, lang: Lang): DiagnosisReport {
  const d = s.diseaseId ? detail(s.diseaseId, lang) : null
  const healthy = !!d?.isHealthy
  let summary = T.summaryUnable[lang]
  if (s.status === 'likely_identified') summary = healthy ? d!.overview : `${d!.overview} ${T.summaryLikely[lang]}`
  if (s.status === 'needs_checking') summary = `${d!.overview} ${T.summaryCheck[lang]}`

  let actions: string[] = d?.management ?? T.unableActions.map((a) => a[lang])
  if (s.status === 'needs_checking') actions = [...T.checkActions.map((a) => a[lang]), ...actions]

  const showSample = s.status === 'likely_identified' && !healthy && d && s.diseaseId?.endsWith('early-blight')

  return {
    id: s.id,
    createdAt: s.createdAt,
    lang,
    crop: s.crop,
    status: s.status,
    disease: d ? { id: d.id, name: d.name, isHealthy: d.isHealthy } : null,
    summary,
    symptoms: d?.symptoms ?? [],
    causes: d?.causes ?? [],
    actions,
    treatment: showSample
      ? { verified: true, products: [sampleMedicine(lang, s.crop, d!.name)] }
      : { verified: false, products: [] },
    prevention: d?.prevention ?? [],
    weather: { summary: T.weatherSummary[lang], points: T.weatherPoints.map((p) => p[lang]), isDemo: true },
    imageUrl: s.imageUrl,
    technical: {
      mode: 'demo',
      note: 'Sample data generated in the browser. No model, knowledge base or weather service was used.',
      crop: s.crop,
      scenario: s.scenario,
      status: s.status,
      diseaseId: s.diseaseId,
    },
    isDemo: true,
  }
}

function sampleWeather(lang: Lang, lat: number, lon: number, label: string | undefined, crop?: CropId): WeatherReport {
  const today = new Date()
  const temps = [31, 30, 29, 28, 29, 30, 29]
  const hums = [78, 80, 84, 88, 86, 82, 83]
  const rains = [0, 2.4, 6.8, 9.1, 3.2, 0, 1.6]
  const daily = temps.map((tempC, i) => {
    const d = new Date(today)
    d.setDate(today.getDate() - (temps.length - i))
    return { date: d.toISOString(), temperatureC: tempC, humidityPct: hums[i], rainfallMm: rains[i] }
  })
  const bn = lang === 'bn'
  return {
    location: { label, latitude: lat, longitude: lon },
    observation: {
      temperatureC: 29.4,
      humidityPct: 83,
      rainfallMm: 23.1,
      periodLabel: bn ? 'গত ৭ দিন (নমুনা)' : 'Last 7 days (sample)',
      observedAt: today.toISOString(),
      isFresh: true,
      freshnessMessage: 'Demo weather data — not live observations.',
    },
    daily,
    cropContext: crop
      ? [
          bn
            ? 'নমুনা বার্তা: উষ্ণ ও আর্দ্র সময়ে পাতার রোগ সহজে ছড়াতে পারে, তাই পাতা ঘন ঘন দেখুন।'
            : 'Sample message: warm, humid periods can help leaf diseases spread, so check your leaves more often.',
        ]
      : [],
    guidance: [
      bn
        ? 'নমুনা বার্তা: ভেজা সকালে পাতার নিচের দিকটা দেখুন।'
        : 'Sample message: on damp mornings, look at the underside of your leaves.',
      bn
        ? 'নমুনা বার্তা: সকালে গাছের গোড়ায় সেচ দিলে পাতা কম ভেজা থাকে।'
        : 'Sample message: watering the base of plants early in the day keeps leaves drier.',
    ],
    source: bn ? 'নমুনা তথ্য — সত্যিকারের পর্যবেক্ষণ নয়' : 'Sample values — not real observations',
    isDemo: true,
  }
}

export const demoApi: CropGuardianApi = {
  async diagnose(input, signal) {
    const [imageUrl] = await Promise.all([resizeImage(input.image), sleep(4200, signal)])
    const outcome = chooseOutcome(input.crop, input.scenario ?? 'auto')
    const stored: Stored = {
      id: `demo-${Date.now().toString(36)}`,
      createdAt: new Date().toISOString(),
      crop: input.crop,
      status: outcome.status,
      diseaseId: outcome.diseaseId,
      imageUrl,
      scenario: input.scenario ?? 'auto',
    }
    writeAll([stored, ...readAll()])
    return buildReport(stored, input.lang)
  },

  async getWeather(q) {
    await sleep(500)
    return sampleWeather(q.lang, q.latitude, q.longitude, undefined, q.crop)
  },

  async updateFieldLocation(loc) {
    return loc
  },

  async listHistory(q) {
    const needle = (q.q ?? '').trim().toLowerCase()
    return readAll()
      .filter((s) => !q.crop || s.crop === q.crop)
      .map<HistoryItem>((s) => {
        const d = s.diseaseId ? detail(s.diseaseId, q.lang) : null
        return {
          id: s.id,
          createdAt: s.createdAt,
          crop: s.crop,
          status: s.status,
          diseaseName: d?.name ?? null,
          isHealthy: !!d?.isHealthy,
          thumbUrl: s.imageUrl,
          isDemo: true,
        }
      })
      .filter((h) => !needle || (h.diseaseName ?? '').toLowerCase().includes(needle) || h.crop.includes(needle))
  },

  async getReport(id, lang) {
    const s = readAll().find((x) => x.id === id)
    if (!s) throw new Error('not-found')
    return buildReport(s, lang)
  },

  async downloadReportPdf() {
    // Demo mode has no PDF generator. The report page opens the browser print dialog ("Save as PDF").
    return 'print'
  },

  async listDiseases(q) {
    await sleep(150)
    return summaries(q.lang, q.crop, q.q)
  },

  async getDisease(id, lang) {
    const d = detail(id, lang)
    if (!d) throw new Error('not-found')
    return d
  },
}
