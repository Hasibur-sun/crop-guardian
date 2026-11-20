
import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import Home from './pages/Home'
import CheckPlant from './pages/CheckPlant'
import Results from './pages/Results'
import Guide from './pages/Guide'
import GuideDetail from './pages/GuideDetail'
import Weather from './pages/Weather'
import History from './pages/History'
import About from './pages/About'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="check" element={<CheckPlant />} />
        <Route path="results/:id" element={<Results />} />
        <Route path="guide" element={<Guide />} />
        <Route path="guide/:id" element={<GuideDetail />} />
        <Route path="weather" element={<Weather />} />
        <Route path="history" element={<History />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
