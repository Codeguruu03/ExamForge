const TYPE_COLORS = {
    duplicate: { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.3)', text: '#ef4444', label: '🔴 Exact Duplicate' },
    near_duplicate: { bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.3)', text: '#f59e0b', label: '🟡 Near-Duplicate' },
}

function PairCard({ pair }) {
    const style = TYPE_COLORS[pair.similarity_type]
    return (
        <div className="p-3 rounded-xl mb-2"
            style={{ background: style.bg, border: `1px solid ${style.border}` }}>
            <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold" style={{ color: style.text }}>{style.label}</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full"
                    style={{ background: style.border, color: style.text }}>
                    {(pair.similarity_score * 100).toFixed(1)}%
                </span>
            </div>
            <div className="space-y-1">
                <p className="text-xs" style={{ color: 'var(--text-primary)' }}>
                    <span className="font-bold" style={{ color: style.text }}>Q{pair.question_id_1}:</span> {pair.question_text_1}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                    <span className="font-bold" style={{ color: style.text }}>Q{pair.question_id_2}:</span> {pair.question_text_2}
                </p>
            </div>
        </div>
    )
}

export default function SimilarityReport({ report }) {
    const allPairs = [...report.duplicate_pairs, ...report.near_duplicate_pairs]
        .sort((a, b) => b.similarity_score - a.similarity_score)

    return (
        <div className="p-5 rounded-2xl" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <h3 className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                🔍 Similarity & Redundancy Report
            </h3>
            <div className="flex gap-4 text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>
                <span>🔴 Duplicates: <strong style={{ color: '#ef4444' }}>{report.duplicate_pairs.length}</strong></span>
                <span>🟡 Near-dups: <strong style={{ color: '#f59e0b' }}>{report.near_duplicate_pairs.length}</strong></span>
                <span>✅ Unique: <strong style={{ color: '#22c55e' }}>{report.unique_question_count}</strong></span>
            </div>

            {allPairs.length === 0 ? (
                <div className="text-center py-8">
                    <div className="text-3xl mb-2">✅</div>
                    <p className="text-sm font-semibold" style={{ color: '#22c55e' }}>No similar questions detected!</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>All {report.total_questions} questions appear unique.</p>
                </div>
            ) : (
                <div className="overflow-y-auto" style={{ maxHeight: '280px' }}>
                    {allPairs.map((pair, i) => (
                        <PairCard key={i} pair={pair} />
                    ))}
                </div>
            )}
        </div>
    )
}
