import { FlaskConical } from 'lucide-react'
import { DEMO_MODE } from '../lib/config'
import { useI18n } from '../i18n'

/** Always visible in demo mode so sample data can never be mistaken for a real diagnosis. */
export function DemoBanner() {
  const { t } = useI18n()
  if (!DEMO_MODE) return null
  return (
    <div className="no-print bg-lime text-deep" role="note">
      <div className="wrap flex items-start gap-2.5 py-2 text-[0.85rem] font-semibold leading-snug sm:items-center sm:justify-center">
        <FlaskConical className="mt-0.5 h-4 w-4 shrink-0 sm:mt-0" aria-hidden="true" />
        <span>{t('common.demoBanner')}</span>
      </div>
    </div>
  )
}
