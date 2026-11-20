import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Download, Search, Sprout } from 'lucide-react'
import { Button } from '../components/Button'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { DEMO_MODE } from '../lib/config'
import { formatDate } from '../lib/format'
import { useAsync } from '../hooks/useAsync'
import { useI18n, type TKey } from '../i18n'
import type { CropId } from '../types/api'

export default function History() {
  const { t, lang } = useI18n()
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [crop, setCrop] = useState<CropId | undefined>()
  const [pdfError, setPdfError] = useState(false)
  const { data, loading, error, reload } = useAsync(() => api.listHistory({ crop, q, lang }), [crop, q, lang])

  const tabs: { id: CropId | undefined; label: string }[] = [
    { id: undefined, label: t('common.all') },
    { id: 'potato', label: t('crop.potato') },
    { id: 'tomato', label: t('crop.tomato') },
    { id: 'rice', label: t('crop.rice') },
    { id: 'brinjal', label: t('crop.brinjal') },
    { id: 'jute', label: t('crop.jute') },
  ]

  async function pdf(id: string) {
    setPdfError(false)
    try {
      const how = await api.downloadReportPdf(id)
      // Demo mode has no PDF service: open the report and use the browser's "Save as PDF".
      if (how === 'print') navigate(`/results/${encodeURIComponent(id)}?print=1`)
    } catch {
      setPdfError(true)
    }
  }

  return (
    <div className="on-light bg-cream">
      <div className="bg-forest text-cream">
        <div className="wrap py-12 md:py-20">
          <p className="eyebrow text-lime">{t('hist.eyebrow')}</p>
          <h1 className="h-section mt-4 max-w-3xl !text-[clamp(2.4rem,6vw,5rem)]">{t('hist.title')}</h1>
          <p className="mt-4 text-lg text-cream/80">{t('hist.sub')}</p>
        </div>
      </div>

      <div className="wrap py-10 md:py-14">
        <div className="flex flex-col gap-5 border-b border-forest/20 pb-6 lg:flex-row lg:items-center lg:justify-between">
          <div role="tablist" className="-mx-5 flex gap-2 overflow-x-auto px-5 pb-1 lg:mx-0 lg:px-0">
            {tabs.map((tab) => {
              const active = crop === tab.id
              return (
                <button
                  key={tab.label}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => setCrop(tab.id)}
                  className={`min-h-[44px] shrink-0 rounded-full border px-5 font-bold transition ${
                    active ? 'border-forest bg-forest text-cream' : 'border-forest/40 text-forest hover:bg-forest/10'
                  }`}
                >
                  {tab.label}
                </button>
              )
            })}
          </div>
          <label className="relative block lg:w-80">
            <span className="sr-only">{t('hist.search')}</span>
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-forest/60" />
            <input
              type="search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={t('hist.search')}
              className="min-h-[48px] w-full rounded-full border border-forest/40 bg-offwhite pl-12 pr-4 text-base placeholder:text-charcoal/50"
            />
          </label>
        </div>

        {pdfError && (
          <p role="alert" className="pt-4 font-semibold text-[#7A1712]">
            {t('hist.pdfErr')}
          </p>
        )}

        {error ? (
          <div className="py-16 text-center">
            <p>{t('common.error')}</p>
            <button type="button" onClick={reload} className="mt-4 font-bold text-forest underline">
              {t('common.tryAgain')}
            </button>
          </div>
        ) : loading && !data ? (
          <p className="py-16 text-center text-lg">{t('common.loading')}</p>
        ) : data && data.length === 0 ? (
          <div className="py-20 text-center">
            <Sprout className="mx-auto h-12 w-12 text-forest/50" />
            <h2 className="mt-4 font-serif text-4xl text-forest">{t('hist.empty')}</h2>
            <p className="mt-2">{t('hist.emptyBody')}</p>
            <Button to="/check" variant="forest" className="mt-8">
              {t('nav.check')}
            </Button>
          </div>
        ) : (
          <ul className="divide-y divide-forest/20">
            {data?.map((h) => (
              <li key={h.id} className="grid items-center gap-4 py-6 md:grid-cols-12 md:gap-6">
                <Link to={`/results/${encodeURIComponent(h.id)}`} className="flex items-center gap-4 md:col-span-6">
                  <span className="h-20 w-20 shrink-0 overflow-hidden bg-forest/10">
                    {h.thumbUrl ? (
                      <img src={h.thumbUrl} alt="" className="h-full w-full object-cover" />
                    ) : (
                      <span className="flex h-full w-full items-center justify-center text-forest/50">
                        <Sprout className="h-8 w-8" />
                      </span>
                    )}
                  </span>
                  <span>
                    <span className="block font-serif text-2xl leading-tight text-forest md:text-3xl">
                      {h.diseaseName ? (h.isHealthy ? t('hist.healthy') : h.diseaseName) : t('hist.unknown')}
                    </span>
                    <span className="block text-charcoal/80">
                      {t(`crop.${h.crop}` as TKey)} · {formatDate(h.createdAt, lang)}
                      {DEMO_MODE && ' · Demo'}
                    </span>
                  </span>
                </Link>
                <div className="md:col-span-2">
                  <StatusBadge status={h.status} />
                </div>
                <div className="flex gap-2 md:col-span-4 md:justify-end">
                  <Button to={`/results/${encodeURIComponent(h.id)}`} variant="forest">
                    {t('hist.open')}
                  </Button>
                  <Button variant="outline" onClick={() => pdf(h.id)} icon={<Download className="h-4 w-4" />}>
                    {t('hist.pdf')}
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
