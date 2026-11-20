import { Link } from 'react-router-dom'
import { ArrowRight, ArrowUpRight, Check, ChevronDown } from 'lucide-react'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { Reveal } from '../components/Reveal'
import { CROPS } from '../lib/crops'
import { summaries } from '../lib/diseaseData'
import { useI18n, type TKey } from '../i18n'

export default function Home() {
  const { t, lang } = useI18n()
  const diseases = summaries(lang).filter((d) => !d.isHealthy).slice(0, 7)

  const steps: { n: string; title: TKey; body: TKey }[] = [
    { n: '01', title: 'home.step1T', body: 'home.step1B' },
    { n: '02', title: 'home.step2T', body: 'home.step2B' },
    { n: '03', title: 'home.step3T', body: 'home.step3B' },
  ]

  return (
    <>
      {/* HERO */}
      <section className="relative overflow-hidden bg-forest text-cream">
        <div className="wrap grid min-h-[calc(100svh-72px-40px)] gap-10 pb-0 pt-10 lg:grid-cols-12 lg:gap-12 lg:pt-14">
          <div className="flex flex-col justify-between gap-10 pb-10 lg:col-span-7 lg:pb-14">
            <p className="eyebrow inline-flex w-fit items-center gap-2 rounded-full border border-cream/25 px-4 py-2 text-sage">
              <span className="h-2 w-2 rounded-full bg-lime" aria-hidden="true" />
              {t('home.badge')}
            </p>

            <h1 className="display">
              <span className="block text-cream">{t('home.hero1')}</span>
              <span className="block text-lime">{t('home.hero2')}</span>
            </h1>

            <div className="flex flex-col gap-8">
              <p className="max-w-md text-lg leading-relaxed text-cream/85">{t('home.heroSub')}</p>
              <div className="flex flex-col gap-3 sm:flex-row">
                <Button to="/check" size="lg" icon={<ArrowRight className="h-5 w-5" />}>
                  {t('home.cta1')}
                </Button>
                <Button to="/guide" size="lg" variant="outlineLight">
                  {t('home.cta2')}
                </Button>
              </div>
            </div>
          </div>

          <div className="relative lg:col-span-5">
            <Photo
              src="hero.jpg"
              kind="terrace"
              alt=""
              className="h-[340px] w-full sm:h-[440px] lg:absolute lg:inset-x-0 lg:bottom-0 lg:top-0 lg:h-auto"
            />
            <Link
              to="/check"
              className="absolute bottom-4 left-4 flex items-center gap-3 bg-cream px-5 py-4 font-semibold text-forest transition hover:bg-lime lg:bottom-8 lg:left-[-2.5rem]"
            >
              {t('nav.check')}
              <ArrowUpRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
        <div className="wrap hidden items-center gap-2 pb-5 text-xs font-bold uppercase tracking-[0.16em] text-sage lg:flex">
          <ChevronDown className="h-4 w-4" /> {t('home.scroll')}
        </div>
      </section>

      {/* INTRO */}
      <section className="on-light bg-cream py-20 md:py-28">
        <div className="wrap grid items-center gap-12 lg:grid-cols-12 lg:gap-20">
          <Reveal className="lg:col-span-5">
            <Photo src="intro.jpg" kind="leaf" className="aspect-[4/5] w-full" />
          </Reveal>
          <Reveal className="lg:col-span-7" delay={120}>
            <p className="eyebrow text-forest/70">{t('home.introEyebrow')}</p>
            <h2 className="h-section mt-4 text-forest">{t('home.introTitle')}</h2>
            <p className="mt-6 max-w-xl text-lg leading-relaxed">{t('home.introBody')}</p>
            <ul className="mt-8 space-y-3 border-t border-forest/20 pt-6">
              {(['home.pt1', 'home.pt2', 'home.pt3'] as TKey[]).map((k) => (
                <li key={k} className="flex items-center gap-3 font-semibold text-forest">
                  <Check className="h-5 w-5 text-forest" /> {t(k)}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="on-light bg-offwhite py-20 md:py-28">
        <div className="wrap">
          <Reveal className="max-w-3xl">
            <p className="eyebrow text-forest/70">{t('home.howEyebrow')}</p>
            <h2 className="h-section mt-4 text-forest">{t('home.howTitle')}</h2>
          </Reveal>
          <div className="mt-14 grid gap-10 md:grid-cols-3 md:gap-8">
            {steps.map((s, i) => (
              <Reveal key={s.n} delay={i * 110}>
                <div className="border-t border-forest/30 pt-6">
                  <span className="font-serif text-6xl leading-none text-forest/25">{s.n}</span>
                  <h3 className="mt-6 font-serif text-3xl leading-tight text-forest">{t(s.title)}</h3>
                  <p className="mt-3 max-w-sm text-[1.05rem] leading-relaxed">{t(s.body)}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* CROPS */}
      <section className="on-light bg-cream py-20 md:py-28">
        <div className="wrap">
          <Reveal className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
            <div>
              <p className="eyebrow text-forest/70">{t('home.cropsEyebrow')}</p>
              <h2 className="h-section mt-4 text-forest">{t('home.cropsTitle')}</h2>
            </div>
            <p className="max-w-sm text-lg">{t('home.cropsBody')}</p>
          </Reveal>
          <div className="mt-12 grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-5 md:gap-x-5">
            {CROPS.map((c, i) => (
              <Reveal key={c.id} delay={i * 70} className={i === 4 ? 'col-span-2 md:col-span-1' : ''}>
                <Link to={`/check?crop=${c.id}`} className="group block">
                  <Photo src={c.photo} kind={c.art} className={`w-full ${i === 4 ? 'aspect-[16/10] md:aspect-[3/4]' : 'aspect-[3/4]'}`} />
                  <div className="mt-4 flex items-center justify-between border-b border-forest/30 pb-3">
                    <span className="font-serif text-2xl text-forest">{t(`crop.${c.id}` as TKey)}</span>
                    <ArrowUpRight className="h-5 w-5 text-forest transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
                  </div>
                </Link>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* KNOWLEDGE */}
      <section className="bg-deep text-cream">
        <div className="grid lg:grid-cols-2">
          <Photo src="knowledge.jpg" kind="tomato" className="min-h-[320px] lg:min-h-[640px]" />
          <div className="flex flex-col justify-center px-5 py-16 sm:px-8 lg:px-16 lg:py-24">
            <Reveal>
              <p className="eyebrow text-lime">{t('home.knowEyebrow')}</p>
              <h2 className="h-section mt-4">{t('home.knowTitle')}</h2>
              <p className="mt-5 max-w-lg text-lg text-cream/80">{t('home.knowBody')}</p>
              <ul className="mt-8 divide-y divide-cream/15 border-y border-cream/15">
                {diseases.map((d) => (
                  <li key={d.id}>
                    <Link to={`/guide/${d.id}`} className="group flex items-center justify-between py-3.5 hover:text-lime">
                      <span className="text-lg">
                        <span className="mr-3 text-sage">{t(`crop.${d.crop}` as TKey)}</span>
                        {d.name}
                      </span>
                      <ArrowRight className="h-5 w-5 opacity-60 transition group-hover:translate-x-1" />
                    </Link>
                  </li>
                ))}
              </ul>
              <Button to="/guide" className="mt-8" icon={<ArrowRight className="h-5 w-5" />}>
                {t('home.cta2')}
              </Button>
            </Reveal>
          </div>
        </div>
      </section>

      {/* WEATHER */}
      <section className="on-light bg-offwhite py-20 md:py-28">
        <div className="wrap grid items-center gap-12 lg:grid-cols-12 lg:gap-20">
          <Reveal className="lg:order-2 lg:col-span-5">
            <Photo src="weather.jpg" kind="rice" className="aspect-[4/5] w-full" />
          </Reveal>
          <Reveal className="lg:col-span-7" delay={120}>
            <p className="eyebrow text-forest/70">{t('home.wxEyebrow')}</p>
            <h2 className="h-section mt-4 text-forest">{t('home.wxTitle')}</h2>
            <p className="mt-6 max-w-xl text-lg leading-relaxed">{t('home.wxBody')}</p>
            <Button to="/weather" variant="forest" className="mt-8" icon={<ArrowRight className="h-5 w-5" />}>
              {t('home.wxCta')}
            </Button>
          </Reveal>
        </div>
      </section>

      {/* CLOSING CTA */}
      <section className="on-light bg-cream py-24 md:py-36">
        <Reveal className="wrap text-center">
          <h2 className="mx-auto max-w-5xl font-serif text-[clamp(2.4rem,6.5vw,5.5rem)] leading-[1.02] text-forest">
            {t('home.ctaTitle')}
          </h2>
          <p className="mx-auto mt-6 max-w-md text-lg">{t('home.ctaBody')}</p>
          <Button to="/check" size="lg" variant="forest" className="mt-10" icon={<ArrowRight className="h-5 w-5" />}>
            {t('home.cta1')}
          </Button>
        </Reveal>
      </section>
    </>
  )
}
