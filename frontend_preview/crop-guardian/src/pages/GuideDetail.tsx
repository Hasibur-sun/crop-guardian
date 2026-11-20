import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, AlertTriangle, ShieldCheck, Sprout } from 'lucide-react'
import { Block, BulletList } from '../components/Lists'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { CROPS } from '../lib/crops'
import { api } from '../lib/api'
import { useAsync } from '../hooks/useAsync'
import { useI18n, type TKey } from '../i18n'

export default function GuideDetail() {
  const { id = '' } = useParams()
  const { t, lang } = useI18n()
  const { data: d, loading, error } = useAsync(() => api.getDisease(id, lang), [id, lang])

  if (loading && !d) return <p className="wrap py-24 text-center font-serif text-3xl text-forest">{t('common.loading')}</p>
  if (error || !d) {
    return (
      <div className="wrap py-24 text-center">
        <h1 className="h-section text-forest">{t('guide.notFound')}</h1>
        <Button to="/guide" variant="forest" className="mt-8">
          {t('guide.all')}
        </Button>
      </div>
    )
  }

  const crop = CROPS.find((c) => c.id === d.crop)
  const name = d.isHealthy ? t('guide.healthy') : d.name

  return (
    <div className="on-light bg-offwhite">
      <section className="bg-forest text-cream">
        <div className="wrap grid gap-10 py-10 md:py-16 lg:grid-cols-12 lg:items-end">
          <div className="lg:col-span-8">
            <Link to="/guide" className="inline-flex items-center gap-2 font-semibold text-sage hover:text-lime">
              <ArrowLeft className="h-4 w-4" /> {t('guide.all')}
            </Link>
            <p className="eyebrow mt-8 text-lime">{t(`crop.${d.crop}` as TKey)}</p>
            <h1 className="mt-3 font-serif text-[clamp(2.6rem,7vw,6rem)] leading-[1.02]">{name}</h1>
            <p className="mt-5 max-w-2xl text-xl text-cream/85">{d.overview}</p>
          </div>
          <Photo src={crop?.photo} kind={crop?.art ?? 'leaf'} className="hidden aspect-[4/3] lg:col-span-4 lg:block" />
        </div>
      </section>

      <div className="wrap pb-12">
        {d.symptoms.length > 0 && (
          <Block title={d.isHealthy ? t('guide.symptomsHealthy') : t('guide.symptoms')}>
            <BulletList items={d.symptoms} />
          </Block>
        )}
        {d.causes.length > 0 && (
          <Block title={t('guide.causes')}>
            <BulletList items={d.causes} />
          </Block>
        )}
        {d.prevention.length > 0 && (
          <Block title={t('guide.prevention')}>
            <BulletList items={d.prevention} />
          </Block>
        )}
        {d.management.length > 0 && (
          <Block title={d.isHealthy ? t('guide.managementHealthy') : t('guide.management')}>
            <BulletList items={d.management} />
          </Block>
        )}

        <Block title={t('guide.medicine')}>
          {d.isHealthy ? (
            <p className="flex items-start gap-3 text-[1.05rem] font-semibold text-forest">
              <Sprout className="mt-1 h-5 w-5 shrink-0" /> {t('guide.healthyCare')}
            </p>
          ) : d.treatment.verified && d.treatment.products.length > 0 ? (
            <div className="space-y-6">
              {d.treatment.products.map((m, i) => (
                <article key={i} className="border border-forest/30 bg-white p-5">
                  <p className="mb-3 inline-flex items-center gap-2 text-sm font-bold text-forest">
                    <ShieldCheck className="h-4 w-4" /> {t('res.verified')}
                  </p>
                  <h3 className="font-serif text-2xl text-forest">{m.name}</h3>
                  <p className="mt-1 text-charcoal/80">
                    {m.activeIngredient} · {m.manufacturer}
                  </p>
                  <p className="mt-4">
                    <strong>{t('res.med.dosage')}:</strong> {m.labelDosage}
                  </p>
                  <p className="mt-2">
                    <strong>{t('res.med.how')}:</strong> {m.applicationInstructions}
                  </p>
                  <p className="mt-2">
                    <strong>{t('res.med.phi')}:</strong> {m.preHarvestInterval}
                  </p>
                  <div className="mt-4">
                    <p className="mb-2 font-bold">{t('res.med.safety')}</p>
                    <BulletList items={m.safetyPrecautions} />
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="flex items-start gap-4 border border-forest/30 bg-cream px-5 py-5">
              <AlertTriangle className="mt-1 h-6 w-6 shrink-0 text-forest" />
              <p className="text-[1.05rem] font-semibold text-forest">{t('res.noMedicine')}</p>
            </div>
          )}
        </Block>

        <div className="border-t border-forest/20 pt-10">
          <Button to={`/check?crop=${d.crop}`} size="lg" variant="forest" icon={<ArrowRight className="h-5 w-5" />}>
            {t('nav.check')}
          </Button>
        </div>
      </div>
    </div>
  )
}
