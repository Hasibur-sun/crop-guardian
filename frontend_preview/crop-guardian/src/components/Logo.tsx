export function LogoMark({ className = 'h-9 w-9' }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="#A7E84B" />
      <path d="M16 5c7 4 9 11 0 21C7 16 9 9 16 5Z" fill="#064C35" />
      <path d="M16 10v15" stroke="#A7E84B" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  )
}

export function Logo({ tone = 'dark' }: { tone?: 'dark' | 'light' }) {
  return (
    <span className="inline-flex items-center gap-3">
      <LogoMark />
      <span className={`font-serif text-[1.45rem] leading-none ${tone === 'light' ? 'text-cream' : 'text-forest'}`}>
        Crop Guardian
      </span>
    </span>
  )
}
