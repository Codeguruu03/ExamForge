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
                    className="p-5 rounded-2xl transition-all duration-200 flex flex-col justify-between"
                    style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full flex items-center justify-center text-xl"
                            style={{ background: `${card.color}20`, color: card.color }}>
                            {card.icon}
                        </div>
                        <div className="text-xs font-semibold tracking-wide uppercase" style={{ color: 'var(--text-secondary)' }}>
                            {card.label}
                        </div>
                    </div>
                    <div className="text-3xl font-extrabold" style={{ color: 'var(--text-primary)' }}>
                        {card.value}
                    </div>
                </div>
            ))}
        </div>
    )
}
