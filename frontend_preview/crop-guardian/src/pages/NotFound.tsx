import { Button } from '../components/Button'
import { useI18n } from '../i18n'

export default function NotFound() {
  const { t } = useI18n()
  return (
    <div className="on-light bg-cream py-28 text-center">
      <div className="wrap">
        <h1 className="h-section text-forest">{t('nf.title')}</h1>
        <p className="mt-4 text-lg">{t('nf.body')}</p>
        <Button to="/" variant="forest" size="lg" className="mt-8">
          {t('nav.homeLabel')}
        </Button>
      </div>
    </div>
  )
}
