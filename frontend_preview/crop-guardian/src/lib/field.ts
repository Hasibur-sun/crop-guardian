import type { FieldLocation } from '../types/api'

const KEY = 'cg.field'

export interface Preset {
  id: string
  en: string
  bn: string
  latitude: number
  longitude: number
}

/** Approximate district centres. Farmers can also enter exact coordinates. */
export const PRESETS: Preset[] = [
  { id: 'dhaka', en: 'Dhaka', bn: 'ঢাকা', latitude: 23.81, longitude: 90.41 },
  { id: 'tangail', en: 'Tangail', bn: 'টাঙ্গাইল', latitude: 24.25, longitude: 89.92 },
  { id: 'mymensingh', en: 'Mymensingh', bn: 'ময়মনসিংহ', latitude: 24.75, longitude: 90.41 },
  { id: 'rajshahi', en: 'Rajshahi', bn: 'রাজশাহী', latitude: 24.37, longitude: 88.6 },
  { id: 'bogura', en: 'Bogura', bn: 'বগুড়া', latitude: 24.85, longitude: 89.37 },
  { id: 'rangpur', en: 'Rangpur', bn: 'রংপুর', latitude: 25.75, longitude: 89.25 },
  { id: 'khulna', en: 'Khulna', bn: 'খুলনা', latitude: 22.82, longitude: 89.55 },
  { id: 'jashore', en: 'Jashore', bn: 'যশোর', latitude: 23.17, longitude: 89.21 },
  { id: 'barishal', en: 'Barishal', bn: 'বরিশাল', latitude: 22.7, longitude: 90.37 },
  { id: 'chattogram', en: 'Chattogram', bn: 'চট্টগ্রাম', latitude: 22.36, longitude: 91.78 },
  { id: 'cumilla', en: 'Cumilla', bn: 'কুমিল্লা', latitude: 23.46, longitude: 91.18 },
  { id: 'sylhet', en: 'Sylhet', bn: 'সিলেট', latitude: 24.9, longitude: 91.87 },
]

export function getField(): FieldLocation | null {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? (JSON.parse(raw) as FieldLocation) : null
  } catch {
    return null
  }
}

export function saveField(loc: FieldLocation) {
  try {
    localStorage.setItem(KEY, JSON.stringify(loc))
  } catch {
    /* storage can be unavailable in private mode; the app still works */
  }
}

/** Rough bounding box of Bangladesh, used to catch typing mistakes. */
export const inBangladesh = (lat: number, lon: number) => lat >= 20.5 && lat <= 26.8 && lon >= 88 && lon <= 92.8
