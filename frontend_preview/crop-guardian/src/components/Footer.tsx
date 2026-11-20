import { Link } from 'react-router-dom'
import { Logo } from './Logo'
import { useI18n } from '../i18n'

export function Footer() {
  const { t } = useI18n()
  const links = [
    { to: '/check', label: t('nav.check') },
    { to: '/guide', label: t('nav.guide') },
    { to: '/weather', label: t('nav.weather') },
    { to: '/history', label: t('nav.history') },
    { to: '/about', label: t('nav.about') },
  ]
  return (
    <footer className="no-print bg-deep text-cream">
      <div className="wrap grid gap-12 py-14 md:grid-cols-12 md:py-20">
        <div className="md:col-span-6">
          <Logo tone="light" />
          <p className="mt-8 max-w-md font-serif text-3xl leading-tight text-lime md:text-4xl">
            {t('home.ctaTitle')}
          </p>
        </div>
        <div className="md:col-span-3">
          <p className="eyebrow text-sage">{t('footer.explore')}</p>
          <ul className="mt-5 space-y-3">
            {links.map((l) => (
              <li key={l.to}>
                <Link to={l.to} className="text-lg hover:text-lime">
                  {l.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <p className="text-sm leading-relaxed text-sage md:col-span-3">{t('footer.disclaimer')}</p>
      </div>
      <div className="border-t border-cream/10">
        <div className="wrap py-6 text-sm text-sage">{t('footer.rights', { year: new Date().getFullYear() })}</div>
      </div>
    </footer>
  )
}
