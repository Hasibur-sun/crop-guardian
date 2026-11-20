import type { ReactNode } from 'react'

export function BulletList({ items, dark = false }: { items: string[]; dark?: boolean }) {
  return (
    <ul className="space-y-3.5">
      {items.map((item, i) => (
        <li key={i} className="flex gap-4 text-[1.05rem]">
          <span className={`mt-[0.72em] h-2 w-2 shrink-0 ${dark ? 'bg-lime' : 'bg-forest'}`} aria-hidden="true" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}

export function NumberList({ items }: { items: string[] }) {
  return (
    <ol className="space-y-5">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-5">
          <span className="font-serif text-4xl leading-none text-forest/80">{String(i + 1).padStart(2, '0')}</span>
          <span className="pt-1 text-[1.05rem]">{item}</span>
        </li>
      ))}
    </ol>
  )
}

/** Editorial section: title on the left, content on the right, a single thin rule above. */
export function Block({ title, children, id }: { title: string; children: ReactNode; id?: string }) {
  return (
    <section id={id} className="grid gap-5 border-t border-forest/20 py-10 md:grid-cols-12 md:gap-10 md:py-14">
      <h2 className="h-section text-forest md:col-span-4 md:!text-[2.1rem]">{title}</h2>
      <div className="md:col-span-8">{children}</div>
    </section>
  )
}
