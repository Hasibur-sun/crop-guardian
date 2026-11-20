import type { CropId } from '../types/api'
import type { ArtKind } from '../components/Art'

export interface CropInfo {
  id: CropId
  photo: string
  art: ArtKind
  /** The current classifier covers potato and tomato. Other crops get guidance as the backend grows. */
  fullGuide: boolean
}

export const CROPS: CropInfo[] = [
  { id: 'potato', photo: 'crop-potato.jpg', art: 'potato', fullGuide: true },
  { id: 'tomato', photo: 'crop-tomato.jpg', art: 'tomato', fullGuide: true },
  { id: 'rice', photo: 'crop-rice.jpg', art: 'rice', fullGuide: false },
  { id: 'brinjal', photo: 'crop-brinjal.jpg', art: 'brinjal', fullGuide: false },
  { id: 'jute', photo: 'crop-jute.jpg', art: 'jute', fullGuide: false },
]

export const isCropId = (v: string | null): v is CropId => !!v && CROPS.some((c) => c.id === v)
