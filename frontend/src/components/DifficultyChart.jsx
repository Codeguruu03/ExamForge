import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    Cell, PieChart, Pie, Legend
} from 'recharts'

const COLORS = {
    Easy: '#22c55e',
    Moderate: '#f59e0b',
    Hard: '#ef4444',
}

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="px-3 py-2 rounded-lg text-sm"
                style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', color: 'var(--text-primary)' }}>
                <p>Q{label}: {payload[0]?.payload?.text?.slice(0, 40)}...</p>
                <p style={{ color: COLORS[payload[0]?.payload?.level] || '#fff' }}>
                    {payload[0]?.name}: {(payload[0]?.value * 100).toFixed(1)}%
                </p>
            </div>
        )
    }
    return null
}

export default function DifficultyChart({ questions }) {
    // Bar chart data — one bar per question
    const barData = questions.map((q, i) => ({
        name: i + 1,
        text: q.text,
        difficulty: typeof q.difficulty_index === 'number' ? q.difficulty_index : null,
        level: typeof q.difficulty_index === 'number'
            ? q.difficulty_index >= 0.8 ? 'Easy' : q.difficulty_index >= 0.4 ? 'Moderate' : 'Hard'
            : 'Unknown',
    })).filter(d => d.difficulty !== null)

    // Pie chart: distribution summary
    const dist = { Easy: 0, Moderate: 0, Hard: 0 }
    questions.forEach(q => {
        if (typeof q.difficulty_index === 'number') {
            if (q.difficulty_index >= 0.8) dist.Easy++
            else if (q.difficulty_index >= 0.4) dist.Moderate++
            else dist.Hard++
        }
    })
    const pieData = Object.entries(dist).map(([name, value]) => ({ name, value })).filter(d => d.value > 0)

    const hasStats = barData.length > 0

    return (
        <div className="p-5 rounded-2xl" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
            <h3 className="font-semibold mb-1" style={{ color: 'var(--text-primary)' }}>
                📊 Difficulty Distribution
            </h3>
            <p className="text-xs mb-4" style={{ color: 'var(--text-secondary)' }}>
                {hasStats ? 'Based on student response data' : 'Upload student responses to see difficulty metrics'}
            </p>

            {hasStats ? (
                <>
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                            <XAxis dataKey="name" tick={{ fill: '#9aa3c0', fontSize: 11 }} label={{ value: 'Question #', position: 'insideBottom', offset: -2, fill: '#9aa3c0', fontSize: 11 }} />
                            <YAxis tick={{ fill: '#9aa3c0', fontSize: 11 }} domain={[0, 1]} tickFormatter={v => `${(v * 100).toFixed(0)}%`} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="difficulty" radius={[4, 4, 0, 0]}>
                                {barData.map((entry, index) => (
                                    <Cell key={index} fill={COLORS[entry.level]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="mt-4">
                        <ResponsiveContainer width="100%" height={120}>
                            <PieChart>
                                <Pie data={pieData} cx="50%" cy="50%" outerRadius={45} dataKey="value" label={({ name, value }) => `${name}: ${value}`} labelLine={false}>
                                    {pieData.map((entry) => (
                                        <Cell key={entry.name} fill={COLORS[entry.name]} />
                                    ))}
                                </Pie>
                                <Legend iconType="circle" wrapperStyle={{ fontSize: 11, color: '#9aa3c0' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </>
            ) : (
                <div className="text-center py-10">
                    <div className="text-4xl mb-3">📈</div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                        Questions extracted successfully.<br />
                        Provide student responses via <code className="text-xs px-1 py-0.5 rounded" style={{ background: 'var(--bg-secondary)', color: 'var(--accent-blue)' }}>POST /api/analyze/</code> to see difficulty metrics.
                    </p>
                </div>
            )}
        </div>
    )
}
