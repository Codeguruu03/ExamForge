import { useState } from 'react'
import UploadPage from './pages/UploadPage'
import Dashboard from './pages/Dashboard'
import './index.css'

export default function App() {
  const [analysisData, setAnalysisData] = useState(null)

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <header style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))' }}>
            <span className="text-white font-bold text-sm">EF</span>
          </div>
          <div>
            <h1 className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
              ExamForge
            </h1>
            <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              Exam Reliability & Question Quality Analyzer
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs px-2 py-1 rounded-full"
              style={{ background: 'rgba(79,125,255,0.15)', color: 'var(--accent-blue)', border: '1px solid rgba(79,125,255,0.3)' }}>
              ● API Ready
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {!analysisData ? (
          <UploadPage onAnalysisComplete={setAnalysisData} />
        ) : (
          <Dashboard data={analysisData} onReset={() => setAnalysisData(null)} />
        )}
      </main>
    </div>
  )
}
