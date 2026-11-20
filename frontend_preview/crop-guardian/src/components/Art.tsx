import type { ReactNode } from 'react'

/**
 * Original botanical artwork used wherever a photograph slot has no image yet.
 * Drop real photos into /public/images (see the README there) to replace them.
 */
export type ArtKind = 'terrace' | 'leaf' | 'tomato' | 'potato' | 'rice' | 'brinjal' | 'jute'

const GREENS = ['#0F5A3C', '#2E7A3A', '#5FA03A', '#8DBE3F', '#B7DB5A']

function Terrace() {
  const ys = Array.from({ length: 11 }, (_, i) => -40 + i * 52)
  return (
    <>
      <rect width="400" height="500" fill="#2E7A3A" />
      {ys.map((y, i) => (
        <path
          key={i}
          d={`M0 ${y} C 110 ${y - 45}, 250 ${y + 45}, 400 ${y - 15} L400 ${y + 70} C 250 ${y + 100}, 110 ${y + 25}, 0 ${y + 80} Z`}
          fill={GREENS[i % GREENS.length]}
        />
      ))}
      <g fill="none" stroke="#0A3323" strokeOpacity=".18" strokeWidth="2">
        {ys.map((y, i) => (
          <path key={i} d={`M0 ${y + 80} C 110 ${y + 25}, 250 ${y + 100}, 400 ${y + 70}`} />
        ))}
      </g>
      <rect x="236" y="196" width="16" height="12" fill="#F5F2E8" />
      <path d="M232 197 L244 188 L256 197Z" fill="#0A3323" />
    </>
  )
}

function Leaf() {
  const veins = Array.from({ length: 8 }, (_, i) => i)
  return (
    <>
      <rect width="400" height="500" fill="#0A3323" />
      <path d="M200 30 C 340 120, 350 340, 200 475 C 50 340, 60 120, 200 30Z" fill="#2E7A3A" />
      <path d="M200 30 C 340 120, 350 340, 200 475 L200 30Z" fill="#5FA03A" opacity=".6" />
      <g stroke="#A7E84B" strokeOpacity=".55" strokeWidth="2" fill="none" strokeLinecap="round">
        <path d="M200 40 L200 470" strokeWidth="3.5" />
        {veins.map((i) => (
          <g key={i}>
            <path d={`M200 ${110 + i * 45} Q 255 ${92 + i * 45}, ${312 - i * 7} ${72 + i * 45}`} />
            <path d={`M200 ${110 + i * 45} Q 145 ${92 + i * 45}, ${88 + i * 7} ${72 + i * 45}`} />
          </g>
        ))}
      </g>
    </>
  )
}

function Tomato() {
  const fruits: [number, number, number][] = [
    [150, 330, 38],
    [245, 380, 34],
    [95, 235, 28],
    [300, 270, 30],
  ]
  return (
    <>
      <rect width="400" height="500" fill="#4E7F47" />
      <rect width="400" height="250" fill="#6B9A52" opacity=".55" />
      <path d="M-10 90 C 120 140, 180 60, 300 150 S 380 300, 420 330" stroke="#1F4A2B" strokeWidth="7" fill="none" />
      <path d="M150 290 C 150 310, 150 320, 150 330 M245 340 C 245 360, 245 370, 245 380 M95 205 L95 235 M300 240 L300 270" stroke="#1F4A2B" strokeWidth="4" fill="none" />
      {[
        [70, 120, -30],
        [200, 105, 20],
        [320, 190, 50],
        [40, 300, -60],
        [350, 380, 10],
        [190, 450, -20],
      ].map(([x, y, r], i) => (
        <ellipse key={i} cx={x} cy={y} rx="46" ry="20" transform={`rotate(${r} ${x} ${y})`} fill="#2F6B3A" />
      ))}
      {fruits.map(([x, y, r], i) => (
        <g key={i}>
          <circle cx={x} cy={y} r={r} fill="#D9382B" />
          <circle cx={x - r * 0.35} cy={y - r * 0.35} r={r * 0.2} fill="#fff" opacity=".35" />
          <path d={`M${x - 10} ${y - r + 3} L${x} ${y - r - 7} L${x + 10} ${y - r + 3} L${x} ${y - r + 9}Z`} fill="#2F6B3A" />
        </g>
      ))}
    </>
  )
}

function Potato() {
  const tubers: [number, number, number, number, number][] = [
    [140, 340, 78, 54, -18],
    [260, 390, 70, 48, 14],
    [210, 270, 58, 40, 30],
  ]
  return (
    <>
      <rect width="400" height="500" fill="#E9E1C9" />
      <rect y="300" width="400" height="200" fill="#D9CDAA" />
      {tubers.map(([x, y, rx, ry, r], i) => (
        <g key={i} transform={`rotate(${r} ${x} ${y})`}>
          <ellipse cx={x + 6} cy={y + 8} rx={rx} ry={ry} fill="#000" opacity=".1" />
          <ellipse cx={x} cy={y} rx={rx} ry={ry} fill="#C9A66B" stroke="#A9844A" strokeWidth="3" />
          {[-0.4, 0.1, 0.5].map((k, j) => (
            <circle key={j} cx={x + rx * k} cy={y + ry * (j - 1) * 0.35} r="4" fill="#8B6B3A" />
          ))}
        </g>
      ))}
      {[
        [90, 90, -40],
        [170, 60, 10],
        [260, 100, 40],
        [330, 60, 70],
      ].map(([x, y, r], i) => (
        <g key={i} transform={`rotate(${r} ${x} ${y})`}>
          <ellipse cx={x} cy={y} rx="52" ry="22" fill="#2F6B3A" />
          <path d={`M${x - 52} ${y} L${x + 52} ${y}`} stroke="#A7E84B" strokeOpacity=".6" strokeWidth="2" />
        </g>
      ))}
    </>
  )
}

function Rice() {
  const stalks = Array.from({ length: 12 }, (_, i) => i)
  return (
    <>
      <rect width="400" height="500" fill="#DCE8B0" />
      <rect y="380" width="400" height="120" fill="#8DBE3F" opacity=".55" />
      {stalks.map((i) => {
        const x0 = 20 + i * 32
        const x1 = 40 + i * 28 + (i % 2) * 14
        return (
          <g key={i}>
            <path d={`M${x0} 500 C ${x0} 340, ${x1 - 20} 240, ${x1} 130`} stroke="#4E8A3A" strokeWidth="3.5" fill="none" />
            {[0, 1, 2, 3, 4, 5, 6].map((j) => (
              <ellipse
                key={j}
                cx={x1 + (j % 2 ? 7 : -7) + j * 1.4}
                cy={130 + j * 14}
                rx="4.5"
                ry="9"
                fill="#D8B84A"
                transform={`rotate(${j % 2 ? 24 : -24} ${x1} ${130 + j * 14})`}
              />
            ))}
          </g>
        )
      })}
    </>
  )
}

function Brinjal() {
  return (
    <>
      <rect width="400" height="500" fill="#CFE0B8" />
      <ellipse cx="200" cy="90" rx="190" ry="60" fill="#5FA03A" opacity=".5" />
      <g>
        <ellipse cx="140" cy="300" rx="50" ry="130" transform="rotate(-14 140 300)" fill="#4A2A5E" />
        <ellipse cx="120" cy="260" rx="9" ry="60" transform="rotate(-14 120 260)" fill="#fff" opacity=".18" />
        <path d="M118 175 C 105 160, 150 150, 170 168 C 160 190, 130 190, 118 175Z" fill="#2F6B3A" />
      </g>
      <g>
        <ellipse cx="278" cy="330" rx="44" ry="115" transform="rotate(12 278 330)" fill="#5B3573" />
        <ellipse cx="294" cy="290" rx="8" ry="52" transform="rotate(12 294 290)" fill="#fff" opacity=".18" />
        <path d="M262 228 C 250 214, 292 205, 312 222 C 302 244, 274 244, 262 228Z" fill="#2F6B3A" />
      </g>
      <path d="M0 80 C 100 20, 300 20, 400 80" stroke="#2F6B3A" strokeWidth="6" fill="none" />
    </>
  )
}

function Jute() {
  const stalks = [60, 125, 195, 265, 335]
  return (
    <>
      <rect width="400" height="500" fill="#C8DDA6" />
      <rect y="400" width="400" height="100" fill="#6F9B48" opacity=".6" />
      {stalks.map((x, i) => (
        <g key={x}>
          <path d={`M${x} 500 L${x + (i % 2 ? 8 : -8)} 40`} stroke="#4E7F3A" strokeWidth="5" />
          {Array.from({ length: 8 }, (_, j) => (
            <ellipse
              key={j}
              cx={x + (j % 2 ? 26 : -26)}
              cy={90 + j * 48}
              rx="30"
              ry="9"
              transform={`rotate(${j % 2 ? -28 : 28} ${x + (j % 2 ? 26 : -26)} ${90 + j * 48})`}
              fill={j % 3 === 0 ? '#3E7A3F' : '#5FA03A'}
            />
          ))}
        </g>
      ))}
    </>
  )
}

const MAP: Record<ArtKind, () => ReactNode> = {
  terrace: Terrace,
  leaf: Leaf,
  tomato: Tomato,
  potato: Potato,
  rice: Rice,
  brinjal: Brinjal,
  jute: Jute,
}

export function Art({ kind, className = '' }: { kind: ArtKind; className?: string }) {
  const Piece = MAP[kind]
  return (
    <svg
      viewBox="0 0 400 500"
      preserveAspectRatio="xMidYMid slice"
      className={`h-full w-full ${className}`}
      aria-hidden="true"
      focusable="false"
    >
      <Piece />
    </svg>
  )
}
