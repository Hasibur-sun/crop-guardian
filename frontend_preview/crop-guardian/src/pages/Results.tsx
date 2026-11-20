import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { AlertTriangle, Download, FlaskConical, History as HistoryIcon, Plus, ShieldCheck } from 'lucide-react'
import { Block, BulletList, NumberList } from '../components/Lists'
import { Button } from '../components/Button'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../lib/api'
import { fetchProtectedImage } from '../lib/api/client'
import { formatDate } from '../lib/format'
import { useAsync } from '../hooks/useAsync'
import { useI18n, type TKey } from '../i18n'
import type { DiagnosisReport, Medicine } from '../types/api'

export default function Results() {
  const { id = '' } = useParams()
  const { t, lang } = useI18n()
  const location = useLocation()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [pdfError, setPdfError] = useState(false)
  const [protectedImageUrl, setProtectedImageUrl] = useState<string | null>(null)

  const passed = (location.state as { report?: DiagnosisReport } | null)?.report
  const { data, error, loading } = useAsync(() => api.getReport(id, lang), [id, lang])
  const report = data ?? (passed && passed.id === id && passed.lang === lang ? passed : null)
// Load the original plant photograph using tester authentication.
useEffect(() => {
  let cancelled = false
  let objectUrl: string | null = null

  setProtectedImageUrl(null)

  if (!report?.imageUrl) return

  fetchProtectedImage(report.imageUrl)
    .then((url) => {
      objectUrl = url

      if (cancelled) {
        URL.revokeObjectURL(url)
      } else {
        setProtectedImageUrl(url)
      }
    })
    .catch((error) => {
      console.error('Unable to load protected plant image:', error)
    })

  return () => {
    cancelled = true
    if (objectUrl) URL.revokeObjectURL(objectUrl)
  }
}, [report?.imageUrl])
  // "Download PDF" from the history page in demo mode opens this page with ?print=1
  useEffect(() => {
  if (
    report &&
    params.get('print') === '1' &&
    (!report.imageUrl || protectedImageUrl)
  ) {
    const timer = setTimeout(() => window.print(), 500)
    return () => clearTimeout(timer)
  }
}, [report, params, protectedImageUrl])

  async function download() {
    setPdfError(false)
    try {
      const how = await api.downloadReportPdf(id)
      if (how === 'print') window.print()
    } catch {
      setPdfError(true)
    }
  }

  if (!report) {
    return (
      <div className="wrap py-24 text-center">
        {loading ? (
          <p className="font-serif text-3xl text-forest">{t('common.loading')}</p>
        ) : (
          <>
            <h1 className="h-section text-forest">{t('res.notFound')}</h1>
            <p className="mx-auto mt-4 max-w-md">{error ? t('res.notFoundBody') : ''}</p>
            <Button to="/check" variant="forest" className="mt-8">
              {t('res.another')}
            </Button>
          </>
        )}
      </div>
    )
  }

  const healthy = !!report.disease?.isHealthy
  const cropName = t(`crop.${report.crop}` as TKey)
  const diseaseName = report.disease ? (healthy ? t('guide.healthy') : report.disease.name) : ''

  let title = t('res.mainUnable')
  if (report.status === 'unable_to_identify' || !report.disease) title = t('res.mainUnable')
  else if (healthy) title = t('res.mainHealthy', { crop: cropName })
  else if (report.status === 'needs_checking') title = t('res.mainCheck', { crop: cropName, disease: diseaseName })
  else title = t('res.mainLikely', { crop: cropName, disease: diseaseName })

  const showTreatment = !healthy
  const tips: TKey[] = ['check.tip1', 'check.tip2', 'check.tip3']

  return (
    <div className="print-plain on-light bg-offwhite">
      {/* A. Main result */}
      <section className="print-plain bg-forest text-cream">
        <div className="wrap grid gap-10 py-12 md:py-20 lg:grid-cols-12">
          <div className="lg:col-span-8">
            <p className="eyebrow text-lime">{t('res.eyebrow')}</p>
            <h1 className="mt-5 font-serif text-[clamp(2.4rem,6vw,5.2rem)] leading-[1.04]">{title}</h1>
            <div className="mt-6 flex flex-wrap items-center gap-4">
              <StatusBadge status={report.status} />
              <span className="text-sage">
                {cropName} · {formatDate(report.createdAt, lang)}
              </span>
            </div>
          </div>
          {report.imageUrl && (
  <figure className="lg:col-span-4">
    {protectedImageUrl ? (
      <img
        src={protectedImageUrl}
        alt={t('res.photo')}
        className="max-h-[320px] w-full object-cover lg:max-h-[360px]"
      />
    ) : (
      <div className="flex min-h-[180px] items-center justify-center bg-white/10 text-sm text-cream">
        {t('common.loading')}
      </div>
    )}

    <figcaption className="mt-2 text-sm text-sage">
      {t('res.photo')}
    </figcaption>
  </figure>
)}
        </div>
      </section>

      <div className="wrap pb-6">
        {report.isDemo && (
          <div role="note" className="-mt-px flex items-start gap-3 bg-lime px-4 py-3 font-semibold text-deep">
            <FlaskConical className="mt-0.5 h-5 w-5 shrink-0" /> {t('res.demoNote')}
          </div>
        )}

        {/* B. What is happening */}
        <Block title={t('res.happening')}>
          <p className="text-xl leading-relaxed">{report.summary}</p>
          {report.status === 'needs_checking' && (
            <p className="mt-4 border-l-4 border-forest pl-4 font-semibold text-forest">{t('res.checkNote')}</p>
          )}
        </Block>

        {/* C. Symptoms */}
        {report.symptoms.length > 0 && (
          <Block title={healthy ? t('res.symptomsHealthy') : t('res.symptoms')}>
            <BulletList items={report.symptoms} />
          </Block>
        )}

        {/* D. Causes: only shown when the knowledge source provided them */}
        {!healthy && report.causes.length > 0 && (
          <Block title={t('res.causes')}>
            <BulletList items={report.causes} />
          </Block>
        )}

        {/* E. Actions */}
        {report.actions.length > 0 && (
          <Block title={healthy ? t('res.actionsHealthy') : t('res.actions')}>
            <NumberList items={report.actions} />
            {report.status === 'unable_to_identify' && (
              <div className="mt-8 border-t border-forest/20 pt-6">
                <p className="font-bold text-forest">{t('res.photoTips')}</p>
                <div className="mt-3">
                  <BulletList items={tips.map((k) => t(k))} />
                </div>
              </div>
            )}
          </Block>
        )}

        {/* F. Treatment and medicine: verified backend data only */}
        {showTreatment && (
          <Block title={t('res.treatment')}>
            {report.treatment.verified && report.treatment.products.length > 0 ? (
              <div className="space-y-8">
                {report.treatment.products.map((m, i) => (
                  <MedicineCard key={i} m={m} />
                ))}
              </div>
            ) : (
              <div className="flex items-start gap-4 border border-forest/30 bg-cream px-5 py-5">
                <AlertTriangle className="mt-1 h-6 w-6 shrink-0 text-forest" />
                <p className="text-[1.05rem] font-semibold text-forest">{t('res.noMedicine')}</p>
              </div>
            )}
          </Block>
        )}

        {/* G. Prevention */}
        {report.prevention.length > 0 && (
          <Block title={t('res.prevention')}>
            <BulletList items={report.prevention} />
          </Block>
        )}

        {/* H. Weather context */}
        {report.weather && (
          <Block title={t('res.weather')}>
            <p className="text-[1.05rem]">{report.weather.summary}</p>
            {report.weather.points.length > 0 && (
              <div className="mt-5">
                <BulletList items={report.weather.points} />
              </div>
            )}
            <p className="mt-5 text-sm text-charcoal/80">{t('res.weatherNote')}</p>
          </Block>
        )}

        {/* I. Actions */}
        <section className="no-print border-t border-forest/20 py-10 md:py-14">
          {pdfError && (
            <p role="alert" className="mb-4 font-semibold text-[#7A1712]">
              {t('res.pdfErr')}
            </p>
          )}
          <div className="flex flex-col gap-3 md:flex-row">
            <Button size="lg" variant="forest" onClick={download} icon={<Download className="h-5 w-5" />}>
              {t('res.download')}
            </Button>
            <Button size="lg" variant="outline" to="/history" icon={<HistoryIcon className="h-5 w-5" />}>
              {t('res.previous')}
            </Button>
            <Button size="lg" variant="lime" onClick={() => navigate('/check')} icon={<Plus className="h-5 w-5" />}>
              {t('res.another')}
            </Button>
          </div>
        </section>

        {/* Technical details, hidden unless opened */}
        <details className="no-print mb-12 border border-forest/20 bg-cream">
          <summary className="cursor-pointer px-5 py-4 font-bold text-forest">{t('common.technical')}</summary>
          <div className="border-t border-forest/20 px-5 py-4">
            <p className="mb-3 text-sm text-charcoal/80">{t('common.technicalHint')}</p>
            <pre className="max-h-96 overflow-auto bg-deep p-4 text-xs leading-relaxed text-cream">
              {JSON.stringify(report.technical, null, 2)}
            </pre>
          </div>
        </details>

        <p className="no-print pb-10 text-sm text-charcoal/70">
          <Link to="/about" className="underline">
            {t('nav.about')}
          </Link>{' '}
          · {t('footer.disclaimer')}
        </p>
      </div>
    </div>
  )
}

function MedicineCard({ m }: { m: Medicine }) {
  const { t } = useI18n()
  const rows: [TKey, string][] = [
    ['res.med.name', m.name],
    ['res.med.active', m.activeIngredient],
    ['res.med.maker', m.manufacturer],
    ['res.med.crop', m.registeredCrop],
    ['res.med.disease', m.registeredDisease],
    ['res.med.dosage', m.labelDosage],
    ['res.med.how', m.applicationInstructions],
    ['res.med.phi', m.preHarvestInterval],
  ]
  return (
    <article className="border border-forest/30 bg-white">
      <header className="flex flex-wrap items-center gap-3 border-b border-forest/20 bg-cream px-5 py-3">
        <span className="inline-flex items-center gap-2 text-sm font-bold text-forest">
          <ShieldCheck className="h-4 w-4" /> {t('res.verified')}
        </span>
        {m.sample && (
          <span className="inline-flex items-center gap-2 bg-lime px-3 py-1 text-sm font-bold text-deep">
            <FlaskConical className="h-4 w-4" /> {t('res.sample')}
          </span>
        )}
      </header>
      <dl className="divide-y divide-forest/10">
        {rows.map(([k, v]) => (
          <div key={k} className="grid gap-1 px-5 py-4 sm:grid-cols-3 sm:gap-6">
            <dt className="text-sm font-bold uppercase tracking-wide text-forest/70">{t(k)}</dt>
            <dd className="sm:col-span-2">{v}</dd>
          </div>
        ))}
        <div className="grid gap-1 px-5 py-4 sm:grid-cols-3 sm:gap-6">
          <dt className="text-sm font-bold uppercase tracking-wide text-forest/70">{t('res.med.safety')}</dt>
          <dd className="sm:col-span-2">
            <BulletList items={m.safetyPrecautions} />
          </dd>
        </div>
      </dl>
    </article>
  )
}
