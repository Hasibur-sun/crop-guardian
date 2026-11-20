import { CheckCircle2, CircleHelp, SearchX } from 'lucide-react'
import type { DiagnosisStatus } from '../types/api'
import { useI18n } from '../i18n'

const STYLE: Record<DiagnosisStatus, string> = {
  likely_identified: 'bg-lime text-deep',
  needs_checking: 'bg-[#EBD58A] text-[#4A3A08]',
  unable_to_identify: 'bg-[#D9D6C8] text-charcoal',
}

export function StatusBadge({ status, className = '' }: { status: DiagnosisStatus; className?: string }) {
  const { t } = useI18n()
  const Icon = status === 'likely_identified' ? CheckCircle2 : status === 'needs_checking' ? CircleHelp : SearchX
  const label =
    status === 'likely_identified' ? t('status.likely') : status === 'needs_checking' ? t('status.check') : t('status.unable')
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-bold ${STYLE[status]} ${className}`}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {label}
    </span>
  )
}
