import StatsOverview from '../components/StatsOverview'
import DifficultyChart from '../components/DifficultyChart'
import QuestionTable from '../components/QuestionTable'
import SimilarityReport from '../components/SimilarityReport'

export default function Dashboard({ data, onReset }) {
    const { normResult, simResult } = data
    const exam = normResult.exam
    const warnings = normResult.warnings || []
    const questions = exam.questions || []

    return (
        <div className="space-y-6">
            {/* Top bar */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                        {exam.title || 'Exam Analysis Report'}
                    </h2>
                    <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                        Source: <span style={{ color: 'var(--accent-blue)' }}>{exam.source_file}</span>
                        &nbsp;·&nbsp;{exam.total_questions} questions extracted
                    </p>
                </div>
                <button
                    onClick={onReset}
                    className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                    style={{ background: 'var(--bg-card)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}
                >
                    ← New Analysis
                </button>
            </div>

            {/* Warnings */}
            {warnings.length > 0 && (
                <div className="p-4 rounded-xl"
                    style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)' }}>
                    <p className="font-semibold text-sm mb-2" style={{ color: 'var(--accent-yellow)' }}>
                        ⚠️ {warnings.length} Warning{warnings.length > 1 ? 's' : ''} from Normalization
                    </p>
                    <ul className="space-y-1">
                        {warnings.map((w, i) => (
                            <li key={i} className="text-xs opacity-80" style={{ color: 'var(--accent-yellow)' }}>• {w}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Stats Overview Cards */}
            <StatsOverview exam={exam} simResult={simResult} />

            {/* Charts + Similarity row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <DifficultyChart questions={questions} />
                <SimilarityReport report={simResult} />
            </div>

            {/* Question Table */}
            <QuestionTable questions={questions} />
        </div>
    )
}
