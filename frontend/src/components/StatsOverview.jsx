const STAT_CARDS = (exam, simResult) => [
    {
        label: 'Total Questions',
        value: exam.total_questions,
        icon: '📝',
        color: 'var(--accent-blue)',
    },
    {
        label: 'Duplicates Found',
        value: simResult.duplicate_pairs.length + simResult.near_duplicate_pairs.length,
        icon: '🔁',
        color: simResult.duplicate_pairs.length > 0 ? 'var(--accent-red)' : 'var(--accent-green)',
    },
    {
        label: 'Unique Questions',
        value: simResult.unique_question_count,
        icon: '✅',
        color: 'var(--accent-green)',
    },
    {
        label: 'Clusters Detected',
        value: simResult.clusters.length,
        icon: '📦',
        color: simResult.clusters.length > 0 ? 'var(--accent-yellow)' : 'var(--accent-green)',
    },
]

export default function StatsOverview({ exam, simResult }) {
    const cards = STAT_CARDS(exam, simResult)

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map((card) => (
                <div key={card.label}
                    className="p-5 rounded-2xl transition-all duration-200"
                    style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                    <div className="text-2xl mb-3">{card.icon}</div>
                    <div className="text-3xl font-extrabold mb-1" style={{ color: card.color }}>
                        {card.value}
                    </div>
                    <div className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>
                        {card.label}
                    </div>
                </div>
            ))}
        </div>
    )
}
