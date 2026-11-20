import { useEffect, useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { Menu, X, ArrowRight } from 'lucide-react'
import { Logo } from './Logo'
import { Button } from './Button'
import { useI18n, type TKey } from '../i18n'
import type { Lang } from '../types/api'

const LINKS: { to: string; key: TKey }[] = [
  { to: '/guide', key: 'nav.guide' },
  { to: '/weather', key: 'nav.weather' },
  { to: '/history', key: 'nav.history' },
  { to: '/about', key: 'nav.about' },
]

function LanguageSwitch({ dark }: { dark: boolean }) {
  const { lang, setLang, t } = useI18n()
  const opts: { id: Lang; label: string }[] = [
    { id: 'en', label: 'EN' },
    { id: 'bn', label: 'বাংলা' },
  ]
  return (
    <div
      role="group"
      aria-label={t('nav.language')}
      className={`inline-flex rounded-full border p-0.5 ${dark ? 'border-cream/30' : 'border-forest/30'}`}
    >
      {opts.map((o) => {
        const active = lang === o.id
        return (
          <button
            key={o.id}
            type="button"
            aria-pressed={active}
            onClick={() => setLang(o.id)}
            className={`min-h-[40px] min-w-[48px] rounded-full px-3 text-sm font-bold transition ${
              active
                ? dark
                  ? 'bg-lime text-deep'
                  : 'bg-forest text-cream'
                : dark
                  ? 'text-cream/80 hover:text-cream'
                  : 'text-forest/70 hover:text-forest'
            }`}
          >
            {o.label}
          </button>
        )
      })}
    </div>
  )
}

export function Navbar() {
  const { t } = useI18n()
  const { pathname } = useLocation()
  const [open, setOpen] = useState(false)
  const dark = pathname === '/'

  useEffect(() => setOpen(false), [pathname])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  return (
    <header
      className={`no-print sticky top-0 z-50 ${
        dark ? 'bg-forest text-cream' : 'on-light border-b border-forest/10 bg-offwhite/90 text-forest backdrop-blur'
      }`}
    >
      <div className="wrap flex h-[72px] items-center justify-between gap-4">
        <Link to="/" aria-label={t('nav.homeLabel')} className="shrink-0">
          <Logo tone={dark ? 'light' : 'dark'} />
        </Link>

        {/* desktop */}
        <nav className="hidden items-center gap-8 lg:flex" aria-label="Main">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `border-b-2 py-1 text-[0.95rem] font-semibold transition ${
                  isActive ? 'border-lime' : 'border-transparent hover:border-current/40'
                }`
              }
            >
              {t(l.key)}
            </NavLink>
          ))}
          <LanguageSwitch dark={dark} />
          <Button to="/check" variant={dark ? 'lime' : 'forest'}>
            {t('nav.check')}
          </Button>
        </nav>

        {/* mobile */}
        <div className="flex items-center gap-2 lg:hidden">
          <LanguageSwitch dark={dark} />
          <button
            type="button"
            onClick={() => setOpen(true)}
            aria-label={t('nav.menu')}
            aria-expanded={open}
            className="flex h-12 w-12 items-center justify-center"
          >
            <Menu className="h-7 w-7" />
          </button>
        </div>
      </div>

      {open && (
        <div className="fixed inset-0 z-[60] flex flex-col overflow-y-auto bg-deep text-cream animate-fade-in lg:hidden">
          <div className="wrap flex h-[72px] shrink-0 items-center justify-between">
            <Logo tone="light" />
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label={t('nav.close')}
              className="flex h-12 w-12 items-center justify-center"
            >
              <X className="h-7 w-7" />
            </button>
          </div>
          <nav className="wrap flex flex-1 flex-col justify-center gap-1 pb-10" aria-label="Mobile">
            {LINKS.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `flex items-center justify-between border-b border-cream/15 py-5 font-serif text-3xl ${
                    isActive ? 'text-lime' : ''
                  }`
                }
              >
                {t(l.key)}
                <ArrowRight className="h-6 w-6 opacity-60" />
              </NavLink>
            ))}
            <Button to="/check" size="lg" className="mt-8 w-full">
              {t('nav.check')}
            </Button>
          </nav>
        </div>
      )}
    </header>
  )
}
