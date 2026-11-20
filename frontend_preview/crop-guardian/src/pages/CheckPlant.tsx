import { useEffect, useRef, useState, type DragEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { AlertTriangle, Camera, Check, ImagePlus, RefreshCw, Sprout, Trash2, Upload } from 'lucide-react'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { api } from '../lib/api'
import { CROPS, isCropId } from '../lib/crops'
import { DEMO_MODE } from '../lib/config'
import { getField } from '../lib/field'
import { useI18n, type TKey } from '../i18n'
import type { CropId, DemoScenario } from '../types/api'

const MAX_BYTES = 10 * 1024 * 1024
const OK_TYPES = ['image/jpeg', 'image/png']
const SCENARIOS: DemoScenario[] = ['auto', 'likely', 'check', 'unable', 'healthy']

export default function CheckPlant() {
  const { t, lang } = useI18n()
  const navigate = useNavigate()
  const [params] = useSearchParams()

  const initialCrop = params.get('crop')
  const [crop, setCrop] = useState<CropId | null>(isCropId(initialCrop) ? initialCrop : null)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [scenario, setScenario] = useState<DemoScenario>('auto')

  const abortRef = useRef<AbortController | null>(null)
  const browseRef = useRef<HTMLInputElement>(null)
  const cameraRef = useRef<HTMLInputElement>(null)

  // Preview URL lifecycle
  useEffect(() => {
    if (!file) {
      setPreview(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  // Friendly progress messages. No fake percentages: the text simply moves on every few seconds.
  useEffect(() => {
    if (!busy) {
      setMsg(0)
      return
    }
    const id = setInterval(() => setMsg((m) => Math.min(m + 1, 2)), 2400)
    return () => clearInterval(id)
  }, [busy])

  function accept(f: File | null | undefined) {
    if (!f) return
    if (!OK_TYPES.includes(f.type)) return setError(t('check.errType'))
    if (f.size > MAX_BYTES) return setError(t('check.errSize'))
    setError(null)
    setFile(f)
  }

  function onDrop(e: DragEvent) {
    e.preventDefault()
    setDragging(false)
    accept(e.dataTransfer.files?.[0])
  }

  async function examine() {
    if (!crop || !file || busy) return
    setBusy(true)
    setError(null)
    const ac = new AbortController()
    abortRef.current = ac
    try {
      const report = await api.diagnose(
        { image: file, crop, lang, location: getField() ?? undefined, scenario },
        ac.signal,
      )
      navigate(`/results/${encodeURIComponent(report.id)}`, { state: { report } })
    } catch (e) {
      if ((e as Error).name !== 'AbortError') setError(t('check.errGeneric'))
      setBusy(false)
    }
  }

  function cancel() {
    abortRef.current?.abort()
    setBusy(false)
  }

  const ready = !!crop && !!file
  const hint = !crop && !file ? t('check.needBoth') : !crop ? t('check.needCrop') : !file ? t('check.needPhoto') : ''
  const loadMessages: TKey[] = ['check.load1', 'check.load2', 'check.load3']

  return (
    <div className="on-light bg-cream">
      <div className="bg-forest text-cream">
        <div className="wrap py-12 md:py-20">
          <p className="eyebrow text-lime">{t('check.eyebrow')}</p>
          <h1 className="h-section mt-4 max-w-3xl !text-[clamp(2.4rem,6vw,5rem)]">{t('check.title')}</h1>
          <p className="mt-4 text-lg text-cream/80">{t('check.sub')}</p>
        </div>
      </div>

      <div className="wrap max-w-5xl py-12 md:py-16">
        {/* STEP 1 */}
        <section aria-labelledby="step1">
          <StepHeading n="1" id="step1" title={t('check.step1')} hint={t('check.step1Hint')} done={!!crop} />
          <div role="radiogroup" aria-labelledby="step1" className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5 md:gap-4">
            {CROPS.map((c, i) => {
              const active = crop === c.id
              return (
                <button
                  key={c.id}
                  type="button"
                  role="radio"
                  aria-checked={active}
                  onClick={() => setCrop(c.id)}
                  className={`group relative self-start text-left transition ${i === 4 ? 'col-span-2 sm:col-span-1' : ''}`}
                >
                  <div className={`relative overflow-hidden ${active ? 'ring-4 ring-forest ring-offset-2 ring-offset-cream' : ''}`}>
                    <Photo src={c.photo} kind={c.art} className="aspect-[4/5] w-full" />
                    {active && (
                      <span className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-lime text-deep">
                        <Check className="h-5 w-5" aria-label={t('check.selected')} />
                      </span>
                    )}
                  </div>
                  <span className="mt-3 block font-serif text-2xl text-forest">{t(`crop.${c.id}` as TKey)}</span>
                  {!c.fullGuide && <span className="block text-sm text-charcoal/70">{t('check.expanding')}</span>}
                </button>
              )
            })}
          </div>
        </section>

        {/* STEP 2 */}
        <section aria-labelledby="step2" className="mt-14 md:mt-20">
          <StepHeading n="2" id="step2" title={t('check.step2')} hint={t('check.upload')} done={!!file} />

          <input
            ref={browseRef}
            type="file"
            accept="image/jpeg,image/png,.jpg,.jpeg,.png"
            className="sr-only"
            tabIndex={-1}
            onChange={(e) => {
              accept(e.target.files?.[0])
              e.target.value = ''
            }}
          />
          <input
            ref={cameraRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="sr-only"
            tabIndex={-1}
            onChange={(e) => {
              accept(e.target.files?.[0])
              e.target.value = ''
            }}
          />

          {!preview ? (
            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={`mt-6 flex flex-col items-center justify-center border-2 border-dashed px-6 py-14 text-center transition md:py-20 ${
                dragging ? 'border-forest bg-lime/30' : 'border-forest/40 bg-offwhite'
              }`}
            >
              <span className="flex h-16 w-16 items-center justify-center rounded-full bg-forest text-lime">
                <ImagePlus className="h-8 w-8" />
              </span>
              <p className="mt-6 font-serif text-3xl text-forest">{t('check.upload')}</p>
              <p className="mt-2 hidden text-charcoal/80 md:block">{t('check.drag')}</p>
              <div className="mt-6 flex w-full max-w-md flex-col gap-3 sm:flex-row sm:justify-center">
                <Button variant="forest" size="lg" onClick={() => browseRef.current?.click()} icon={<Upload className="h-5 w-5" />}>
                  {t('check.browse')}
                </Button>
                <Button variant="outline" size="lg" onClick={() => cameraRef.current?.click()} icon={<Camera className="h-5 w-5" />}>
                  {t('check.camera')}
                </Button>
              </div>
              <p className="mt-5 text-sm text-charcoal/70">{t('check.formats')}</p>
            </div>
          ) : (
            <div className="mt-6 grid gap-6 md:grid-cols-12">
              <div className="relative overflow-hidden bg-deep md:col-span-7">
                <img src={preview} alt={t('check.previewAlt')} className="max-h-[520px] w-full object-contain" />
              </div>
              <div className="flex flex-col justify-between gap-6 md:col-span-5">
                <div className="flex flex-col gap-3">
                  <Button variant="outline" onClick={() => browseRef.current?.click()} icon={<RefreshCw className="h-5 w-5" />}>
                    {t('check.replace')}
                  </Button>
                  <Button variant="outline" onClick={() => setFile(null)} icon={<Trash2 className="h-5 w-5" />}>
                    {t('check.remove')}
                  </Button>
                </div>
                <p className="truncate text-sm text-charcoal/70">{file?.name}</p>
              </div>
            </div>
          )}

          <div className="mt-8 border-t border-forest/20 pt-6">
            <p className="font-bold text-forest">{t('check.tipsTitle')}</p>
            <ul className="mt-3 grid gap-2 text-[0.98rem] md:grid-cols-3 md:gap-6">
              {(['check.tip1', 'check.tip2', 'check.tip3'] as TKey[]).map((k) => (
                <li key={k} className="flex gap-3">
                  <Sprout className="mt-1 h-4 w-4 shrink-0 text-forest" /> {t(k)}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* STEP 3 */}
        <section aria-labelledby="step3" className="mt-14 md:mt-20">
          <StepHeading n="3" id="step3" title={t('check.step3')} done={false} />

          {DEMO_MODE && (
            <label className="mt-6 block max-w-sm text-sm">
              <span className="font-bold text-forest">{t('check.demoLabel')}</span>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value as DemoScenario)}
                className="mt-1 min-h-[48px] w-full border border-forest/40 bg-offwhite px-3 text-base"
              >
                {SCENARIOS.map((s) => (
                  <option key={s} value={s}>
                    {t(`check.demo.${s}` as TKey)}
                  </option>
                ))}
              </select>
            </label>
          )}

          {error && (
            <div role="alert" className="mt-6 flex items-start gap-3 border-l-4 border-[#B3261E] bg-white px-4 py-4 text-[#7A1712]">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" /> {error}
            </div>
          )}

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Button size="lg" variant="forest" disabled={!ready || busy} onClick={examine} className="w-full sm:w-auto sm:min-w-[280px]" icon={<Sprout className="h-5 w-5" />}>
              {t('check.examine')}
            </Button>
            {!ready && <p className="text-charcoal/80">{hint}</p>}
          </div>
        </section>
      </div>

      {busy && (
        <div
          className="fixed inset-0 z-[70] flex flex-col items-center justify-center bg-deep px-6 text-center text-cream animate-fade-in"
          role="alertdialog"
          aria-modal="true"
          aria-live="polite"
          aria-label={t('check.examine')}
        >
          <div className="relative flex h-40 w-40 items-end justify-center" aria-hidden="true">
            <svg viewBox="0 0 120 120" className="h-full w-full">
              <circle cx="60" cy="60" r="56" fill="none" stroke="#A7E84B" strokeOpacity=".25" strokeWidth="2" />
              <g className="origin-[60px_100px] animate-grow">
                <path d="M60 100 V46" stroke="#A7E84B" strokeWidth="4" strokeLinecap="round" />
                <path d="M60 70 C40 70 28 58 28 42 C46 42 58 52 60 70Z" fill="#A7E84B" />
                <path d="M60 58 C80 58 92 46 92 30 C74 30 62 40 60 58Z" fill="#A7E84B" opacity=".85" />
              </g>
            </svg>
          </div>
          <p key={msg} className="mt-10 animate-fade-up font-serif text-3xl md:text-4xl">
            {t(loadMessages[msg])}
          </p>
          <button
            type="button"
            onClick={cancel}
            className="mt-12 min-h-[48px] rounded-full border border-cream/40 px-6 font-semibold text-cream hover:bg-cream hover:text-forest"
          >
            {t('common.cancel')}
          </button>
        </div>
      )}
    </div>
  )
}

function StepHeading({ n, id, title, hint, done }: { n: string; id: string; title: string; hint?: string; done: boolean }) {
  return (
    <div className="flex items-start gap-4 border-t border-forest/30 pt-5">
      <span
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full font-serif text-2xl ${
          done ? 'bg-lime text-deep' : 'bg-forest text-cream'
        }`}
      >
        {done ? <Check className="h-5 w-5" /> : n}
      </span>
      <div>
        <h2 id={id} className="font-serif text-3xl leading-tight text-forest md:text-4xl">
          {title}
        </h2>
        {hint && <p className="mt-1 text-charcoal/80">{hint}</p>}
      </div>
    </div>
  )
}
