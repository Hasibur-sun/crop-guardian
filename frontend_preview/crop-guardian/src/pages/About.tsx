import { ArrowRight, ShieldCheck } from 'lucide-react'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { Reveal } from '../components/Reveal'
import { useI18n, type TKey } from '../i18n'

export default function About() {
  const { t } = useI18n()
  const principles: { n: string; title: TKey; body: TKey }[] = [
    { n: '01', title: 'about.p1T', body: 'about.p1B' },
    { n: '02', title: 'about.p2T', body: 'about.p2B' },
    { n: '03', title: 'about.p3T', body: 'about.p3B' },
  ]
  return (
    <div className="on-light">
      <section className="bg-forest text-cream">
        <div className="wrap grid gap-10 py-12 md:py-20 lg:grid-cols-12 lg:items-end">
          <div className="lg:col-span-7">
            <p className="eyebrow text-lime">{t('about.eyebrow')}</p>
            <h1 className="mt-4 font-serif text-[clamp(2.4rem,6vw,5rem)] leading-[1.05]">{t('about.title')}</h1>
            <p className="mt-6 max-w-xl text-lg text-cream/85">{t('about.intro')}</p>
          </div>
          <Photo src="about.jpg" kind="terrace" className="aspect-[4/3] lg:col-span-5" />
        </div>
      </section>

      <section className="bg-cream py-16 md:py-24">
        <div className="wrap grid gap-10 md:grid-cols-3 md:gap-8">
          {principles.map((p, i) => (
            <Reveal key={p.n} delay={i * 100}>
              <div className="border-t border-forest/30 pt-6">
                <span className="font-serif text-6xl leading-none text-forest/25">{p.n}</span>
                <h2 className="mt-6 font-serif text-3xl text-forest">{t(p.title)}</h2>
                <p className="mt-3 text-[1.05rem]">{t(p.body)}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="bg-offwhite py-16 md:py-24">
        <div className="wrap grid gap-10 md:grid-cols-12 md:gap-16">
          <Reveal className="md:col-span-6">
            <ShieldCheck className="h-10 w-10 text-forest" />
            <h2 className="h-section mt-5 text-forest">{t('about.honestTitle')}</h2>
            <p className="mt-5 text-lg leading-relaxed">{t('about.honestBody')}</p>
          </Reveal>
          <Reveal className="md:col-span-6" delay={120}>
            <h2 className="font-serif text-3xl text-forest">{t('about.cropsTitle')}</h2>
            <p className="mt-4 text-lg leading-relaxed">{t('about.cropsBody')}</p>
            <Button to="/check" variant="forest" size="lg" className="mt-8" icon={<ArrowRight className="h-5 w-5" />}>
              {t('nav.check')}
            </Button>
          </Reveal>
        </div>
      </section>
    </div>
  )
}
