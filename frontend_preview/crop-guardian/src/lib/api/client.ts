
import { API_BASE_URL } from '../config'
import type {
  CropGuardianApi,
  DiagnosisReport,
  DiseaseDetail,
  DiseaseSummary,
  FieldLocation,
  HistoryItem,
  WeatherReport,
} from '../../types/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

// --------------------------------------------------
// TESTER AUTHENTICATION
// --------------------------------------------------

const TOKEN_KEY = 'crop_guardian_tester_token'

export function getTesterToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function saveTesterToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearTesterToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export async function loginTester(accessCode: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ access_code: accessCode }),
  })

  if (!response.ok) {
    if (response.status === 401) throw new Error('Invalid access code.')
    if (response.status === 429) throw new Error('Too many attempts. Try again later.')
    throw new Error(`Login failed (${response.status}).`)
  }

  const data = await response.json()

  if (!data.access_token) {
    throw new Error('The server did not return an access token.')
  }

  saveTesterToken(data.access_token)
}

// --------------------------------------------------
// REQUEST HELPERS
// --------------------------------------------------

function qs(params: Record<string, string | number | undefined>): string {
  const sp = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      sp.set(key, String(value))
    }
  })

  const result = sp.toString()
  return result ? `?${result}` : ''
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  const token = getTesterToken()

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
    })
  } catch (error) {
    if ((error as Error).name === 'AbortError') throw error
    throw new ApiError('Network connection failed.', 0)
  }

  if (response.status === 401) {
    clearTesterToken()
    window.dispatchEvent(new Event('crop-guardian-auth-expired'))
    throw new ApiError('Tester login expired. Please log in again.', 401)
  }

  if (!response.ok) {
    throw new ApiError(`Request failed (${response.status}).`, response.status)
  }

  return (await response.json()) as T
}

// --------------------------------------------------
// AUTHENTICATED IMAGE HELPER
// --------------------------------------------------


export async function fetchProtectedImage(path: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    throw new ApiError(
      `Image request failed (${response.status}).`,
      response.status
    )
  }

  const blob = await response.blob()
  return URL.createObjectURL(blob)
}


// --------------------------------------------------
// LIVE API
// --------------------------------------------------

export const liveApi: CropGuardianApi = {
  diagnose(input, signal) {
    const body = new FormData()

    body.append('image', input.image)
    body.append('crop', input.crop)
    body.append('lang', input.lang)

    if (input.location) {
      body.append('latitude', String(input.location.latitude))
      body.append('longitude', String(input.location.longitude))
    }

    return request<DiagnosisReport>(
      '/api/diagnose',
      { method: 'POST', body, signal },
    )
  },

  getWeather(q) {
    return request<WeatherReport>(
      `/api/weather${qs({
        latitude: q.latitude,
        longitude: q.longitude,
        crop: q.crop,
        lang: q.lang,
      })}`,
    )
  },

  updateFieldLocation(loc) {
    return request<FieldLocation>('/api/weather/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loc),
    })
  },

  listHistory(q) {
    return request<HistoryItem[]>(
      `/api/history${qs({ crop: q.crop, q: q.q, lang: q.lang })}`,
    )
  },

  getReport(id, lang) {
    return request<DiagnosisReport>(
      `/api/history/${encodeURIComponent(id)}${qs({ lang })}`,
    )
  },

  async downloadReportPdf(_id) {
    return 'print'
  },

  listDiseases(q) {
    return request<DiseaseSummary[]>(
      `/api/diseases${qs({ crop: q.crop, q: q.q, lang: q.lang })}`,
    )
  },

  getDisease(id, lang) {
    return request<DiseaseDetail>(
      `/api/diseases/${encodeURIComponent(id)}${qs({ lang })}`,
    )
  },
}
