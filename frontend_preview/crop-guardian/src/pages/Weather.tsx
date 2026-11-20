
import { useState } from 'react'
import {
  Droplets,
  FlaskConical,
  MapPin,
  Thermometer,
  CloudRain,
  Info,
} from 'lucide-react'
import { Button } from '../components/Button'
import { BulletList } from '../components/Lists'
import { api } from '../lib/api'
import { CROPS } from '../lib/crops'
import { getField, inBangladesh, PRESETS, saveField } from '../lib/field'
import { formatNumber, formatShortDate } from '../lib/format'
import { useAsync } from '../hooks/useAsync'
import { useI18n, type TKey } from '../i18n'
import type { CropId, FieldLocation } from '../types/api'

export default function Weather() {
  const { t, lang } = useI18n()

  const [field, setField] = useState<FieldLocation | null>(getField())
  const [crop, setCrop] = useState<CropId | ''>('')
  const [preset, setPreset] = useState('')
  const [lat, setLat] = useState('')
  const [lon, setLon] = useState('')
  const [coordError, setCoordError] = useState(false)
  const [updatingWeather, setUpdatingWeather] = useState(false)
  const [updateError, setUpdateError] = useState(false)

  const { data, loading, error, reload } = useAsync(
    () =>
      field
        ? api.getWeather({
            latitude: field.latitude,
            longitude: field.longitude,
            crop: crop || undefined,
            lang,
          })
        : Promise.resolve(null),
    [field?.latitude, field?.longitude, crop, lang],
  )

  async function commit(loc: FieldLocation) {
    saveField(loc)
    setField(loc)

    try {
      await api.updateFieldLocation(loc)
    } catch {
      /* The location is still saved on this device. */
    }
  }

  async function refreshWeather() {
    if (!field) return

    setUpdatingWeather(true)
    setUpdateError(false)

    try {
      await api.updateFieldLocation({
        latitude: field.latitude,
        longitude: field.longitude,
      })

      await reload()
    } catch {
      setUpdateError(true)
    } finally {
      setUpdatingWeather(false)
    }
  }

  function savePreset() {
    const p = PRESETS.find((x) => x.id === preset)

    if (p) {
      commit({
        label: lang === 'bn' ? p.bn : p.en,
        latitude: p.latitude,
        longitude: p.longitude,
      })
    }
  }

  function saveCoords() {
    const la = parseFloat(lat)
    const lo = parseFloat(lon)

    if (
      Number.isNaN(la) ||
      Number.isNaN(lo) ||
      !inBangladesh(la, lo)
    ) {
      return setCoordError(true)
    }

    setCoordError(false)
    commit({ latitude: la, longitude: lo })
  }

  const fieldName = field
    ? field.label ?? `${field.latitude.toFixed(2)}, ${field.longitude.toFixed(2)}`
    : ''

  const observation = data?.observation

  const hasValidObservation =
    observation?.isFresh === true &&
    observation.temperatureC !== null &&
    observation.temperatureC !== undefined &&
    observation.humidityPct !== null &&
    observation.humidityPct !== undefined &&
    observation.rainfallMm !== null &&
    observation.rainfallMm !== undefined

  return (
    <div className="on-light bg-cream">
      <div className="bg-forest text-cream">
        <div className="wrap py-12 md:py-20">
          <p className="eyebrow text-lime">{t('wx.eyebrow')}</p>

          <h1 className="h-section mt-4 max-w-3xl !text-[clamp(2.4rem,6vw,5rem)]">
            {t('wx.title')}
          </h1>

          <p className="mt-4 max-w-xl text-lg text-cream/80">
            {t('wx.sub')}
          </p>
        </div>
      </div>

      <div className="wrap py-12 md:py-16">
        {/* Field location */}
        <section className="grid gap-8 border-b border-forest/20 pb-12 md:grid-cols-12 md:gap-12">
          <div className="md:col-span-4">
            <h2 className="font-serif text-3xl text-forest">
              {t('wx.yourField')}
            </h2>

            <p className="mt-3 flex items-start gap-2 text-[1.05rem]">
              <MapPin className="mt-1 h-5 w-5 shrink-0 text-forest" />

              <span className={field ? 'font-bold text-forest' : ''}>
                {field ? fieldName : t('wx.none')}
              </span>
            </p>
          </div>

          <div className="md:col-span-8">
            <div className="flex flex-col gap-3 sm:flex-row">
              <label className="flex-1">
                <span className="sr-only">{t('wx.select')}</span>

                <select
                  value={preset}
                  onChange={(e) => setPreset(e.target.value)}
                  className="min-h-[56px] w-full border border-forest/40 bg-offwhite px-4 text-base"
                >
                  <option value="">{t('wx.select')}</option>

                  {PRESETS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {lang === 'bn' ? p.bn : p.en}
                    </option>
                  ))}
                </select>
              </label>

              <Button
                variant="forest"
                size="lg"
                disabled={!preset}
                onClick={savePreset}
              >
                {t('wx.save')}
              </Button>
            </div>

            <details className="mt-5">
              <summary className="cursor-pointer font-bold text-forest">
                {t('wx.advanced')}
              </summary>

              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <label className="block text-sm font-bold text-forest">
                  {t('wx.lat')}

                  <input
                    inputMode="decimal"
                    value={lat}
                    onChange={(e) => setLat(e.target.value)}
                    placeholder="23.81"
                    className="mt-1 min-h-[48px] w-full border border-forest/40 bg-offwhite px-3 text-base font-normal"
                  />
                </label>

                <label className="block text-sm font-bold text-forest">
                  {t('wx.lon')}

                  <input
                    inputMode="decimal"
                    value={lon}
                    onChange={(e) => setLon(e.target.value)}
                    placeholder="90.41"
                    className="mt-1 min-h-[48px] w-full border border-forest/40 bg-offwhite px-3 text-base font-normal"
                  />
                </label>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={saveCoords}
                    className="w-full"
                  >
                    {t('wx.save')}
                  </Button>
                </div>
              </div>

              {coordError && (
                <p role="alert" className="mt-3 font-semibold text-[#7A1712]">
                  {t('wx.badCoords')}
                </p>
              )}
            </details>
          </div>
        </section>

        {field && (
          <>
            {/* Crop selector */}
            <section className="flex flex-col gap-3 border-b border-forest/20 py-8 sm:flex-row sm:items-center sm:gap-6">
              <label htmlFor="wx-crop" className="font-bold text-forest">
                {t('wx.crop')}
              </label>

              <select
                id="wx-crop"
                value={crop}
                onChange={(e) => setCrop(e.target.value as CropId | '')}
                className="min-h-[48px] border border-forest/40 bg-offwhite px-4 text-base sm:min-w-[240px]"
              >
                <option value="">{t('wx.anyCrop')}</option>

                {CROPS.map((c) => (
                  <option key={c.id} value={c.id}>
                    {t(`crop.${c.id}` as TKey)}
                  </option>
                ))}
              </select>
            </section>

            {error ? (
              <div className="py-16 text-center">
                <p>{t('wx.err')}</p>

                <button
                  type="button"
                  onClick={reload}
                  className="mt-4 font-bold text-forest underline"
                >
                  {t('common.tryAgain')}
                </button>
              </div>
            ) : loading && !data ? (
              <p className="py-16 text-center font-serif text-3xl text-forest">
                {t('common.loading')}
              </p>
            ) : data ? (
              <>
                {/* Recent weather */}
                <section className="border-b border-forest/20 py-12">
                  <div className="flex flex-wrap items-baseline justify-between gap-3">
                    <h2 className="font-serif text-3xl text-forest md:text-4xl">
                      {t('wx.recent')}
                    </h2>

                    <p className="text-charcoal/80">
                      {data.observation.periodLabel}
                    </p>
                  </div>

                  {data.isDemo && (
                    <p className="mt-4 inline-flex items-center gap-2 bg-lime px-3 py-1.5 text-sm font-bold text-deep">
                      <FlaskConical className="h-4 w-4" />
                      {data.source}
                    </p>
                  )}

                  {hasValidObservation ? (
                    <dl className="mt-8 grid gap-px bg-forest/20 sm:grid-cols-3">
                      <Metric
                        icon={<Thermometer />}
                        label={t('wx.temp')}
                        value={`${formatNumber(observation.temperatureC!, lang, 1)}°C`}
                      />

                      <Metric
                        icon={<Droplets />}
                        label={t('wx.humidity')}
                        value={`${formatNumber(observation.humidityPct!, lang)}%`}
                      />

                      <Metric
                        icon={<CloudRain />}
                        label={t('wx.rain')}
                        value={`${formatNumber(observation.rainfallMm!, lang, 1)} mm`}
                      />
                    </dl>
                  ) : (
                    <p className="mt-8 border border-forest/30 bg-white p-5 font-semibold text-forest">
                      {data.observation.isFresh
                         ? 'Some recent weather measurements are unavailable.'
                         : data.observation.freshnessMessage}
                    </p>
                  )}

                  <p className="mt-6 flex items-start gap-3 text-[0.98rem]">
                    <Info className="mt-1 h-5 w-5 shrink-0 text-forest" />
                    {t('wx.notDiagnosis')}
                  </p>

                  <div className="mt-5">
                    <Button
                      variant="forest"
                      onClick={refreshWeather}
                      disabled={updatingWeather || loading}
                    >
                      {updatingWeather
                        ? 'Updating weather...'
                        : 'Update Weather'}
                    </Button>

                    {updateError && (
                      <p role="alert" className="mt-3 font-semibold text-[#7A1712]">
                        Weather update failed. Please try again.
                      </p>
                    )}
                  </div>
                </section>

                {/* Meaning for crops */}
                <section className="grid gap-6 border-b border-forest/20 py-12 md:grid-cols-12 md:gap-12">
                  <h2 className="font-serif text-3xl text-forest md:col-span-4">
                    {t('wx.means')}
                  </h2>

                  <div className="space-y-8 md:col-span-8">
                    {data.cropContext.length > 0 ? (
                      <BulletList items={data.cropContext} />
                    ) : (
                      <p>{t('wx.noContext')}</p>
                    )}

                    {data.guidance.length > 0 && (
                      <div>
                        <p className="mb-3 font-bold text-forest">
                          {t('wx.guidance')}
                        </p>

                        <BulletList items={data.guidance} />
                      </div>
                    )}
                  </div>
                </section>

                {/* Daily */}
                {data.daily.length > 0 && (
                  <section className="py-12">
                    <h2 className="font-serif text-3xl text-forest">
                      {t('wx.daily')}
                    </h2>

                    <ul className="mt-6 divide-y divide-forest/15 border-y border-forest/15">
                      {data.daily.map((d) => (
                        <li
                          key={d.date}
                          className="grid grid-cols-4 items-center gap-2 py-3.5 text-[0.98rem]"
                        >
                          <span className="font-bold text-forest">
                            {formatShortDate(d.date, lang)}
                          </span>

                          <span>
                            {d.temperatureC !== null
                              ? `${formatNumber(d.temperatureC, lang, 0)}°C`
                              : '—'}
                          </span>

                          <span>
                            {d.humidityPct !== null
                              ? `${formatNumber(d.humidityPct, lang)}%`
                              : '—'}
                          </span>

                          <span>
                            {d.rainfallMm !== null
                              ? `${formatNumber(d.rainfallMm, lang, 1)} mm`
                              : '—'}
                          </span>
                        </li>
                      ))}
                    </ul>

                    <p className="mt-4 text-sm text-charcoal/70">
                      {t('wx.source')}: {data.source}
                    </p>
                  </section>
                )}
              </>
            ) : null}
          </>
        )}
      </div>
    </div>
  )
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-offwhite p-6 md:p-8">
      <div className="flex items-center gap-2 text-forest [&>svg]:h-5 [&>svg]:w-5">
        {icon}
        <dt className="font-bold">{label}</dt>
      </div>

      <dd className="mt-3 font-serif text-5xl text-forest md:text-6xl">
        {value}
      </dd>
    </div>
  )
}
