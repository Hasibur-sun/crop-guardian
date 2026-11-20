import { DEMO_MODE } from '../config'
import { demoApi } from './demo'
import { liveApi } from './client'
import type { CropGuardianApi } from '../../types/api'

/**
 * The single entry point every page uses.
 * Demo mode and live mode share the same interface (CropGuardianApi),
 * so switching to the real backend needs no page changes.
 */
export const api: CropGuardianApi = DEMO_MODE ? demoApi : liveApi

export { ApiError } from './client'
