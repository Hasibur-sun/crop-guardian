import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Navbar } from './Navbar'
import { Footer } from './Footer'
import { DemoBanner } from './DemoBanner'
import { useI18n } from '../i18n'

export function Layout() {
  const { t } = useI18n()
  const { pathname } = useLocation()

  // Start every page at the top.
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'auto' })
  }, [pathname])

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main"
        className="no-print sr-only z-[100] bg-lime px-4 py-3 font-bold text-deep focus:not-sr-only focus:fixed focus:left-3 focus:top-3"
      >
        {t('common.skip')}
      </a>
      <DemoBanner />
      <Navbar />
      <main id="main" className="flex-1">
        {/* key forces a gentle fade-up on every page change */}
        <div key={pathname} className="animate-fade-up">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  )
}
