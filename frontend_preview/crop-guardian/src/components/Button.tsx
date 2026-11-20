import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

type Variant = 'lime' | 'forest' | 'outline' | 'outlineLight' | 'cream'

interface Props {
  children: ReactNode
  variant?: Variant
  size?: 'md' | 'lg'
  to?: string
  onClick?: () => void
  disabled?: boolean
  type?: 'button' | 'submit'
  className?: string
  icon?: ReactNode
  ariaLabel?: string
}

const VARIANTS: Record<Variant, string> = {
  lime: 'bg-lime text-deep hover:bg-[#b9f060]',
  forest: 'bg-forest text-cream hover:bg-deep',
  cream: 'bg-cream text-forest hover:bg-white',
  outline: 'border border-forest/40 text-forest hover:bg-forest hover:text-cream',
  outlineLight: 'border border-cream/50 text-cream hover:bg-cream hover:text-forest',
}

export function Button({
  children,
  variant = 'lime',
  size = 'md',
  to,
  onClick,
  disabled,
  type = 'button',
  className = '',
  icon,
  ariaLabel,
}: Props) {
  const cls = `inline-flex items-center justify-center gap-2.5 whitespace-nowrap rounded-full font-bold transition duration-200 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-45 ${
    size === 'lg' ? 'min-h-[56px] px-8 text-[1.05rem]' : 'min-h-[48px] px-6 text-[0.98rem]'
  } ${VARIANTS[variant]} ${className}`

  if (to && !disabled) {
    return (
      <Link to={to} className={cls} aria-label={ariaLabel}>
        {children}
        {icon}
      </Link>
    )
  }
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={cls} aria-label={ariaLabel}>
      {children}
      {icon}
    </button>
  )
}
