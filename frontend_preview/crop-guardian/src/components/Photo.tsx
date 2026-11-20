import { useState } from 'react'
import { Art, type ArtKind } from './Art'

interface Props {
  /** File name inside /public/images, e.g. "hero.jpg". Falls back to artwork if it is missing. */
  src?: string
  kind: ArtKind
  alt?: string
  className?: string
}

export function Photo({ src, kind, alt = '', className = '' }: Props) {
  const [failed, setFailed] = useState(!src)
  return (
    <div className={`hover-zoom relative overflow-hidden bg-sage/30 ${className}`}>
      {failed ? (
        <div className="absolute inset-0">
          <Art kind={kind} />
        </div>
      ) : (
        <img
          src={`/images/${src}`}
          alt={alt}
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
          className="absolute inset-0 h-full w-full object-cover"
        />
      )}
    </div>
  )
}
