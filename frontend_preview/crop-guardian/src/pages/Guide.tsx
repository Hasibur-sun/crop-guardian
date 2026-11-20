import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowUpRight, Search } from 'lucide-react'
import { api } from '../lib/api'
import { useAsync } from '../hooks/useAsync'
import { useI18n, type TKey } from '../i18n'
import type { CropId } from '../types/api'

export default function Guide() {
  const { t, lang } = useI18n()
  const [q, setQ] = useState('')
  const [crop, setCrop] = useState<CropId | undefined>()
  const { data, loading, error, reload } = useAsync(() => api.listDiseases({ crop, q, lang }), [crop, q, lang])

  const tabs: { id: CropId | undefined; label: string }[] = [
    { id: undefined, label: t('common.all') },
    { id: 'potato', label: t('crop.potato') },
    { id: 'tomato', label: t('crop.tomato') },
  ]

  return (
    <div className="on-light bg-cream">
      <div className="bg-forest text-cream">
        <div className="wrap py-12 md:py-20">
          <p className="eyebrow text-lime">{t('guide.eyebrow')}</p>
          <h1 className="h-section mt-4 max-w-3xl !text-[clamp(2.4rem,6vw,5rem)]">{t('guide.title')}</h1>
          <p className="mt-4 max-w-xl text-lg text-cream/80">{t('guide.sub')}</p>
        </div>
      </div>

      <div className="wrap py-10 md:py-14">
        <div className="flex flex-col gap-5 border-b border-forest/20 pb-6 md:flex-row md:items-center md:justify-between">
          <div role="tablist" className="flex gap-2">
            {tabs.map((tab) => {
              const active = crop === tab.id
              return (
                <button
                  key={tab.label}
                  type="button"
                  role="tab"
                  aria-selected={active}
                  onClick={() => setCrop(tab.id)}
                  className={`min-h-[44px] rounded-full border px-5 font-bold transition ${
                    active ? 'border-forest bg-forest text-cream' : 'border-forest/40 text-forest hover:bg-forest/10'
                  }`}
                >
                  {tab.label}
                </button>
              )
            })}
          </div>
          <label className="relative block md:w-80">
            <span className="sr-only">{t('guide.search')}</span>
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-forest/60" />
            <input
              type="search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder={t('guide.search')}
              className="min-h-[48px] w-full rounded-full border border-forest/40 bg-offwhite pl-12 pr-4 text-base placeholder:text-charcoal/50"
            />
          </label>
        </div>

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
          <p className="py-16 text-center text-lg">{t('guide.empty')}</p>
        ) : (
          <ul className="divide-y divide-forest/20">
            {data?.map((d) => (
              <li key={d.id}>
                <Link
                  to={`/guide/${d.id}`}
                  className="group grid items-center gap-2 py-6 md:grid-cols-12 md:gap-8 md:py-8"
                >
                  <span className="eyebrow text-forest/70 md:col-span-2">{t(`crop.${d.crop}` as TKey)}</span>
                  <span className="font-serif text-3xl leading-tight text-forest transition group-hover:underline md:col-span-4 md:text-4xl">
                    {d.isHealthy ? t('guide.healthy') : d.name}
                  </span>
                  <span className="md:col-span-5">{d.blurb}</span>
                  <ArrowUpRight className="hidden h-6 w-6 justify-self-end text-forest transition group-hover:translate-x-1 group-hover:-translate-y-1 md:block" />
                </Link>
              </li>
            ))}
          </ul>
        )}

        <p className="mt-10 border-l-4 border-forest pl-4 text-[0.98rem]">{t('guide.soon')}</p>
      </div>
    </div>
  )
}
