/**
 * CTTStatsPanel — shown when student response CSV was uploaded.
 * Displays Cronbach's Alpha, reliability label, and per-question
 * stat rows (difficulty, discrimination, distractor summary).
 */

const DISC_COLOR = {
    Excellent: '#22c55e',
    Good: '#4f7dff',
    Fair: '#f59e0b',
    Poor: '#f97316',
    Remove: '#ef4444',
}

const DIFF_COLOR = {
    Easy: '#22c55e',
    Moderate: '#f59e0b',
    Hard: '#ef4444',
}

const ALPHA_COLOR = (a) => {
    if (a >= 0.9) return '#22c55e'
    if (a >= 0.7) return '#4f7dff'
    if (a >= 0.5) return '#f59e0b'
    return '#ef4444'
}

function StatBadge({ label, color }) {
    return (
        <span className="text-xs px-2 py-0.5 rounded-full font-medium"
            style={{ background: color + '22', color, border: `1px solid ${color}44` }}>
            {label}
        </span>
    )
}

function AlphaGauge({ alpha, label }) {
    const pct = Math.max(0, Math.min(1, alpha)) * 100
    const color = ALPHA_COLOR(alpha)
    return (
        <div className="p-5 rounded-2xl"
            style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', flex: 1 }}>
            <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
                CRONBACH'S α — RELIABILITY
            </p>
            <div className="flex items-end gap-3 mb-3">
                <span className="text-4xl font-extrabold" style={{ color }}>{alpha}</span>
                <span className="mb-1 text-sm font-semibold" style={{ color }}>{label}</span>
            </div>
            <div className="h-2 rounded-full overflow-hidden"
                style={{ background: 'var(--bg-secondary)' }}>
                <div className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${pct}%`, background: color }} />
            </div>
            <div className="flex justify-between mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span>0  Unacceptable</span>
                <span>1  Excellent</span>
            </div>
        </div>
    )
}

export default function CTTStatsPanel({ stats }) {
    const flagged = stats.question_stats.filter(q => q.is_flagged)

    return (
        <div className="space-y-4">
            {/* Reliability + summary row */}
            <div className="flex gap-4 flex-wrap">
                <AlphaGauge alpha={stats.cronbach_alpha} label={stats.reliability_label} />

                <div className="p-5 rounded-2xl"
                    style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', flex: 1 }}>
                    <p className="text-xs font-semibold mb-3" style={{ color: 'var(--text-secondary)' }}>
                        EXAM SUMMARY
                    </p>
                    <div className="grid grid-cols-2 gap-3">
                        {[
                            { label: 'Students', value: stats.total_students },
                            { label: 'Avg Score', value: `${stats.average_score} / ${stats.total_questions}` },
                            { label: 'Std Dev', value: stats.score_std_dev },
                            {
                                label: '⚑ Flagged Qs', value: stats.flagged_question_count,
                                color: stats.flagged_question_count > 0 ? '#ef4444' : '#22c55e'
                            },
                        ].map(item => (
                            <div key={item.label}>
                                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{item.label}</p>
                                <p className="font-bold text-lg" style={{ color: item.color || 'var(--text-primary)' }}>
                                    {item.value}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Flagged questions alert */}
            {flagged.length > 0 && (
                <div className="p-4 rounded-xl"
                    style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)' }}>
                    <p className="font-semibold text-sm mb-2" style={{ color: '#ef4444' }}>
                        ⚑ {flagged.length} Question{flagged.length > 1 ? 's' : ''} Flagged for Review
                    </p>
                    <div className="space-y-2">
                        {flagged.map(q => (
                            <div key={q.question_id} className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                                <span className="font-bold" style={{ color: 'var(--text-primary)' }}>Q{q.question_id}:</span>
                                &nbsp;{q.question_text.slice(0, 60)}…
                                <div className="flex gap-2 mt-1 flex-wrap">
                                    {q.flag_reasons.map((r, i) => (
                                        <span key={i} className="px-2 py-0.5 rounded"
                                            style={{ background: 'rgba(239,68,68,0.15)', color: '#ef4444' }}>
                                            {r}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Per-question stat table */}
            <div className="rounded-2xl overflow-hidden"
                style={{ border: '1px solid var(--border)', background: 'var(--bg-card)' }}>
                <div className="px-5 py-3" style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-secondary)' }}>
                    <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>
                        📈 Per-Question CTT Metrics
                    </p>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                {['Q#', 'Difficulty (p)', 'Level', 'Discrimination (D)', 'Quality', 'Flagged'].map(h => (
                                    <th key={h} className="px-4 py-2 text-left text-xs font-semibold"
                                        style={{ color: 'var(--text-secondary)' }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {stats.question_stats.map(q => (
                                <tr key={q.question_id}
                                    style={{ borderBottom: '1px solid var(--border)' }}>
                                    <td className="px-4 py-2 font-bold text-xs"
                                        style={{ color: 'var(--text-secondary)' }}>Q{q.question_id}</td>
                                    <td className="px-4 py-2 font-mono text-sm">
                                        {(q.difficulty_index * 100).toFixed(1)}%
                                    </td>
                                    <td className="px-4 py-2">
                                        <StatBadge label={q.difficulty_label} color={DIFF_COLOR[q.difficulty_label]} />
                                    </td>
                                    <td className="px-4 py-2 font-mono text-sm">
                                        {q.discrimination_index.toFixed(3)}
                                    </td>
                                    <td className="px-4 py-2">
                                        <StatBadge label={q.discrimination_label} color={DISC_COLOR[q.discrimination_label]} />
                                    </td>
                                    <td className="px-4 py-2">
                                        {q.is_flagged
                                            ? <StatBadge label="⚑ Yes" color="#ef4444" />
                                            : <StatBadge label="✓ OK" color="#22c55e" />}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
