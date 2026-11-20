/** Central runtime configuration, read from Vite environment variables. */
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const flag = import.meta.env.VITE_DEMO_MODE

/** Demo mode is on when VITE_DEMO_MODE=true, or when no API address is configured. */
export const DEMO_MODE: boolean = flag !== undefined && flag !== '' ? flag === 'true' : !API_BASE_URL
