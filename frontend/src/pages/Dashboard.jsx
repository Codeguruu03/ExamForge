import StatsOverview from '../components/StatsOverview'
import DifficultyChart from '../components/DifficultyChart'
import QuestionTable from '../components/QuestionTable'
import SimilarityReport from '../components/SimilarityReport'
import CTTStatsPanel from '../components/CTTStatsPanel'

export default function Dashboard({ data, onReset }) {
    const { normResult, simResult, statsResult } = data
    const exam = normResult.exam
    const warnings = normResult.warnings || []
    const questions = exam.questions || []

    const handleExport = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2))
        const dlAnchorElem = document.createElement('a')
        dlAnchorElem.setAttribute("href", dataStr)
        dlAnchorElem.setAttribute("download", `exam_report_${exam.exam_id || 'export'}.json`)
        dlAnchorElem.click()
    }

    return (
        <div className="space-y-6">
            {/* Top bar */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                        {exam.title || 'Exam Analysis Report'}
                    </h2>
                    <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                        Source: <span style={{ color: 'var(--accent-blue)' }}>{exam.source_file}</span>
                        &nbsp;·&nbsp;{exam.total_questions} questions
                        {statsResult && (
                            <span> · <span style={{ color: 'var(--accent-green)' }}>
                                {statsResult.total_students} students · α = {statsResult.cronbach_alpha}
                            </span></span>
                        )}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button onClick={handleExport} className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                        style={{ background: 'var(--accent-blue)', color: 'white', border: '1px solid var(--accent-blue)' }}>
                        📥 Export Report (JSON)
                    </button>
                    <button onClick={onReset} className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                        style={{ background: 'var(--bg-card)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
                        ← New Analysis
                    </button>
                </div>
            </div>

            {/* Warnings */}
            {warnings.length > 0 && (
                <div className="p-4 rounded-xl max-h-40 overflow-y-auto"
                    style={{ background: 'rgba(234, 179, 8, 0.05)', border: '1px solid rgba(234, 179, 8, 0.15)' }}>
                    <p className="font-semibold text-sm mb-2 flex items-center gap-2" style={{ color: 'var(--accent-yellow)' }}>
                        <span>⚠️</span> {warnings.length} Parser Warning{warnings.length > 1 ? 's' : ''} (Missing Options)
                    </p>
                    <ul className="space-y-1">
                        {warnings.map((w, i) => (
                            <li key={i} className="text-xs opacity-75 font-mono" style={{ color: 'var(--accent-yellow)' }}>• {w}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* KPI Cards */}
            <StatsOverview exam={exam} simResult={simResult} statsResult={statsResult} />

            {/* CTT Stats panel (only if student responses were uploaded) */}
            {statsResult && <CTTStatsPanel stats={statsResult} />}

            {/* Charts + Similarity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DifficultyChart questions={statsResult ? statsResult.question_stats : questions} hasStats={!!statsResult} />
                <SimilarityReport report={simResult} />
            </div>

            {/* Question Table */}
            <QuestionTable questions={questions} statsResult={statsResult} />
        </div>
    )
}
