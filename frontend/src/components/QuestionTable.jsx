import { useState } from 'react'

function Badge({ label, color }) {
    const COLORS = {
        green: { bg: 'rgba(34,197,94,0.15)', text: '#22c55e', border: 'rgba(34,197,94,0.3)' },
        red: { bg: 'rgba(239,68,68,0.15)', text: '#ef4444', border: 'rgba(239,68,68,0.3)' },
        yellow: { bg: 'rgba(245,158,11,0.15)', text: '#f59e0b', border: 'rgba(245,158,11,0.3)' },
        blue: { bg: 'rgba(79,125,255,0.15)', text: 'var(--accent-blue)', border: 'rgba(79,125,255,0.3)' },
    }
    const s = COLORS[color] || COLORS.blue
    return (
        <span className="text-xs px-2 py-0.5 rounded-full font-medium"
            style={{ background: s.bg, color: s.text, border: `1px solid ${s.border}` }}>
            {label}
        </span>
    )
}

function OptionRow({ opt, correctLabel }) {
    const isCorrect = opt.label === (correctLabel || '').toUpperCase()
    return (
        <li className="flex items-start gap-2 text-xs py-0.5">
            <span className="font-bold w-4 shrink-0" style={{ color: isCorrect ? '#22c55e' : 'var(--text-secondary)' }}>
                {opt.label}.
            </span>
            <span style={{ color: isCorrect ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                {opt.text}
            </span>
            {isCorrect && (
                <span className="ml-auto text-xs px-1 rounded" style={{ background: 'rgba(34,197,94,0.15)', color: '#22c55e' }}>✓</span>
            )}
        </li>
    )
}

export default function QuestionTable({ questions }) {
    const [expanded, setExpanded] = useState(null)
    const [filter, setFilter] = useState('all') // 'all' | 'flagged' | 'no-answer'

    const filtered = questions.filter(q => {
        if (filter === 'flagged') return q.is_flagged
        if (filter === 'no-answer') return !q.correct_option
        return true
    })

    return (
        <div className="rounded-2xl overflow-hidden" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            {/* Header */}
            <div className="px-5 py-4 flex items-center justify-between flex-wrap gap-3"
                style={{ borderBottom: '1px solid var(--border)' }}>
                <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    📋 Question Bank ({questions.length})
                </h3>
                <div className="flex gap-2">
                    {[['all', 'All'], ['flagged', '⚑ Flagged'], ['no-answer', 'No Answer Key']].map(([val, lbl]) => (
                        <button key={val} onClick={() => setFilter(val)}
                            className="text-xs px-3 py-1 rounded-lg transition-all"
                            style={{
                                background: filter === val ? 'var(--accent-blue)' : 'var(--bg-secondary)',
                                color: filter === val ? 'white' : 'var(--text-secondary)',
                                border: `1px solid ${filter === val ? 'var(--accent-blue)' : 'var(--border)'}`,
                            }}>
                            {lbl}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr style={{ background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border)' }}>
                            {['#', 'Question', 'Options', 'Answer', 'Status'].map(h => (
                                <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                                    style={{ color: 'var(--text-secondary)' }}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length === 0 && (
                            <tr>
                                <td colSpan={5} className="px-4 py-8 text-center text-sm"
                                    style={{ color: 'var(--text-secondary)' }}>
                                    No questions match this filter.
                                </td>
                            </tr>
                        )}
                        {filtered.map((q) => (
                            <>
                                <tr
                                    key={q.id}
                                    onClick={() => setExpanded(expanded === q.id ? null : q.id)}
                                    className="cursor-pointer transition-colors"
                                    style={{
                                        borderBottom: '1px solid var(--border)',
                                        background: expanded === q.id ? 'var(--bg-card-hover)' : 'transparent',
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                                    onMouseLeave={e => e.currentTarget.style.background = expanded === q.id ? 'var(--bg-card-hover)' : 'transparent'}
                                >
                                    <td className="px-4 py-4 font-bold text-xs w-12" style={{ color: 'var(--text-secondary)' }}>
                                        Q{q.id}
                                    </td>
                                    <td className="px-4 py-3 max-w-xs">
                                        <p className="text-sm font-medium overflow-hidden" style={{ color: 'var(--text-primary)', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                                            {q.text}
                                        </p>
                                    </td>
                                    <td className="px-4 py-3 text-xs text-center" style={{ color: 'var(--text-secondary)' }}>
                                        {q.options?.length || 0}
                                    </td>
                                    <td className="px-4 py-3">
                                        {q.correct_option
                                            ? <Badge label={`Option ${q.correct_option}`} color="green" />
                                            : <Badge label="Not Provided" color="yellow" />}
                                    </td>
                                    <td className="px-4 py-3">
                                        {q.is_flagged
                                            ? <Badge label="⚑ Flagged" color="red" />
                                            : <Badge label="✓ OK" color="green" />}
                                    </td>
                                </tr>
                                {expanded === q.id && (
                                    <tr key={`${q.id}-detail`} style={{ background: 'var(--bg-secondary)' }}>
                                        <td colSpan={5} className="px-6 py-4">
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div>
                                                    <p className="text-xs font-semibold mb-2" style={{ color: 'var(--text-secondary)' }}>OPTIONS</p>
                                                    <ul className="space-y-1">
                                                        {q.options?.map(opt => (
                                                            <OptionRow key={opt.label} opt={opt} correctLabel={q.correct_option} />
                                                        ))}
                                                    </ul>
                                                </div>
                                                {q.is_flagged && q.flag_reason && (
                                                    <div>
                                                        <p className="text-xs font-semibold mb-2" style={{ color: '#ef4444' }}>FLAG REASON</p>
                                                        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{q.flag_reason}</p>
                                                    </div>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
