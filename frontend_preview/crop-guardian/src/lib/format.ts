import type { Lang } from '../types/api'

export function formatDate(iso: string, lang: Lang): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString(lang === 'bn' ? 'bn-BD' : 'en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function formatShortDate(iso: string, lang: Lang): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString(lang === 'bn' ? 'bn-BD' : 'en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
}

export function formatNumber(n: number, lang: Lang, digits = 0): string {
  return n.toLocaleString(lang === 'bn' ? 'bn-BD' : 'en-GB', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}
