import { useCallback, useEffect, useRef, useState } from 'react'

interface State<T> {
  data: T | null
  error: unknown
  loading: boolean
}

/** Tiny data-loading hook. Re-runs whenever `deps` change and ignores out-of-date responses. */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[]) {
  const [state, setState] = useState<State<T>>({ data: null, error: null, loading: true })
  const run = useRef(0)

  const load = useCallback(() => {
    const id = ++run.current
    setState((s) => ({ ...s, loading: true, error: null }))
    fn().then(
      (data) => id === run.current && setState({ data, error: null, loading: false }),
      (error) => id === run.current && setState({ data: null, error, loading: false }),
    )
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    load()
    return () => {
      run.current++
    }
  }, [load])

  return { ...state, reload: load }
}
