import { useState, useCallback } from 'react'
import axios from 'axios'

const EXAM_TYPES = '.pdf,.docx,.txt,.csv,.jpg,.jpeg,.png,.tiff,.bmp,.gif'
const RESP_TYPES = '.csv'

export default function UploadPage({ onAnalysisComplete }) {
    const [examFile, setExamFile] = useState(null)
    const [csvFile, setCsvFile] = useState(null)
    const [answerKey, setAnswerKey] = useState('')   // "1:C,2:A,3:B,4:D"
    const [dragging, setDragging] = useState('')   // 'exam' | 'csv' | ''
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState('')
    const [error, setError] = useState('')

    /* ── Handlers ────────────────────────────────────────────────────────────── */
    const onDrop = useCallback((zone, e) => {
        e.preventDefault(); setDragging('')
        const f = e.dataTransfer.files[0]
        if (!f) return
        zone === 'exam' ? setExamFile(f) : setCsvFile(f)
        setError('')
    }, [])

    const handleSubmit = async () => {
        if (!examFile) return
        setLoading(true); setError('')

        try {
            /* Step 1 — Upload + normalize */
            setStep('📄 Extracting and normalizing questions...')
            const form = new FormData()
            form.append('file', examFile)
            const { data: normResult } = await axios.post('/api/upload/', form)

            /* Step 2 — Similarity detection */
            setStep('🔍 Detecting duplicate questions...')
            const { data: simResult } = await axios.post('/api/similarity/', {
                exam: normResult.exam,
            })

            /* Step 3 (optional) — CTT analysis if CSV provided */
            let statsResult = null
            if (csvFile && answerKey.trim()) {
                setStep('📊 Running CTT statistical analysis...')

                // Parse "1:C,2:A,3:B" → {1:"C",2:"A",3:"B"}
                const correctAnswers = {}
                answerKey.split(',').forEach(pair => {
                    const [q, a] = pair.split(':').map(s => s.trim())
                    if (q && a) correctAnswers[q] = a.toUpperCase()
                })

                const respForm = new FormData()
                respForm.append('exam_json', JSON.stringify(normResult.exam))
                respForm.append('correct_answers_json', JSON.stringify(correctAnswers))
                respForm.append('file', csvFile)
                const { data } = await axios.post('/api/responses/upload', respForm)
                statsResult = data
            }

            setStep('✅ Done!')
            onAnalysisComplete({ normResult, simResult, statsResult })

        } catch (err) {
            setError(err.response?.data?.detail || err.message || 'Unknown error')
        } finally {
            setLoading(false); setStep('')
        }
    }

    /* ── UI ─────────────────────────────────────────────────────────────────── */
    return (
        <div className="max-w-2xl mx-auto pt-8">
            {/* Hero */}
            <div className="text-center mb-10">
                <h2 className="text-4xl font-extrabold mb-3"
                    style={{
                        background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
                        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
                    }}>
                    Analyze Your Exam
                </h2>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Upload a document to extract questions, detect duplicates, and measure quality.
                </p>
            </div>

            {/* Step 1 — Exam file */}
            <StepCard number="1" title="Upload Exam Document" subtitle="PDF, DOCX, JPG, PNG, TXT">
                <DropZone
                    file={examFile}
                    accept={EXAM_TYPES}
                    dragging={dragging === 'exam'}
                    onDragOver={e => { e.preventDefault(); setDragging('exam') }}
                    onDragLeave={() => setDragging('')}
                    onDrop={e => onDrop('exam', e)}
                    onChange={e => { setExamFile(e.target.files[0]); setError('') }}
                    id="examInput"
                    icon="📂"
                    placeholder="Drop your exam file here"
                />
            </StepCard>

            {/* Step 2 — Optional CSV */}
            <StepCard number="2" title="Upload Student Responses" subtitle="Optional — CSV for CTT analysis"
                badge="Optional">
                <DropZone
                    file={csvFile}
                    accept={RESP_TYPES}
                    dragging={dragging === 'csv'}
                    onDragOver={e => { e.preventDefault(); setDragging('csv') }}
                    onDragLeave={() => setDragging('')}
                    onDrop={e => onDrop('csv', e)}
                    onChange={e => { setCsvFile(e.target.files[0]); setError('') }}
                    id="csvInput"
                    icon="📊"
                    placeholder="Drop student response CSV here"
                    compact
                />
                {csvFile && (
                    <div className="mt-3">
                        <label className="text-xs font-semibold block mb-1"
                            style={{ color: 'var(--text-secondary)' }}>
                            Answer Key &nbsp;
                            <span style={{ color: 'var(--text-secondary)', fontWeight: 400 }}>
                                (format: 1:C,2:A,3:B,4:D)
                            </span>
                        </label>
                        <input
                            type="text"
                            placeholder="1:C,2:A,3:B,4:D"
                            value={answerKey}
                            onChange={e => setAnswerKey(e.target.value)}
                            className="w-full px-3 py-2 rounded-lg text-sm"
                            style={{
                                background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                                color: 'var(--text-primary)', outline: 'none'
                            }}
                        />
                    </div>
                )}
            </StepCard>

            {/* Status / Error */}
            {loading && (
                <div className="mt-5 p-4 rounded-xl text-center"
                    style={{ background: 'rgba(79,125,255,0.1)', border: '1px solid rgba(79,125,255,0.3)' }}>
                    <div className="animate-pulse text-sm" style={{ color: 'var(--accent-blue)' }}>{step}</div>
                </div>
            )}
            {error && (
                <div className="mt-5 p-4 rounded-xl"
                    style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
                    <p className="font-semibold text-sm" style={{ color: 'var(--accent-red)' }}>❌ Error</p>
                    <p className="text-xs mt-1 opacity-80" style={{ color: 'var(--accent-red)' }}>{error}</p>
                </div>
            )}

            {/* Submit */}
            <button
                onClick={handleSubmit}
                disabled={!examFile || loading}
                className="w-full mt-6 py-4 rounded-xl font-bold text-lg transition-all"
                style={{
                    background: examFile && !loading
                        ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))' : 'var(--bg-card)',
                    color: examFile && !loading ? 'white' : 'var(--text-secondary)',
                    cursor: examFile && !loading ? 'pointer' : 'not-allowed',
                    border: 'none', opacity: loading ? 0.7 : 1,
                }}>
                {loading ? '⏳ Processing...' : '🚀 Analyze Exam'}
            </button>

            {/* Feature cards */}
            <div className="grid grid-cols-3 gap-4 mt-8">
                {[
                    { icon: '📃', label: 'OCR + Parsing', desc: 'Any format, including scanned' },
                    { icon: '📊', label: 'CTT Metrics', desc: 'Difficulty, discrimination, alpha' },
                    { icon: '🔍', label: 'Duplicates', desc: 'TF-IDF similarity clustering' },
                ].map(c => (
                    <div key={c.label} className="p-4 rounded-xl text-center"
                        style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                        <div className="text-2xl mb-2">{c.icon}</div>
                        <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{c.label}</p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{c.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}

/* ── Sub-components ──────────────────────────────────────────────────────────── */

function StepCard({ number, title, subtitle, badge, children }) {
    return (
        <div className="mb-5 rounded-2xl overflow-hidden"
            style={{ border: '1px solid var(--border)', background: 'var(--bg-card)' }}>
            <div className="px-5 py-3 flex items-center gap-3"
                style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-secondary)' }}>
                <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{ background: 'var(--accent-blue)', color: 'white' }}>
                    {number}
                </span>
                <span className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{title}</span>
                <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{subtitle}</span>
                {badge && (
                    <span className="ml-auto text-xs px-2 py-0.5 rounded-full"
                        style={{
                            background: 'rgba(245,158,11,0.15)', color: 'var(--accent-yellow)',
                            border: '1px solid rgba(245,158,11,0.3)'
                        }}>
                        {badge}
                    </span>
                )}
            </div>
            <div className="p-4">{children}</div>
        </div>
    )
}

function DropZone({ file, accept, dragging, onDragOver, onDragLeave, onDrop, onChange, id, icon, placeholder, compact }) {
    return (
        <div onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
            onClick={() => document.getElementById(id).click()}
            className="rounded-xl text-center cursor-pointer transition-all"
            style={{
                border: `2px dashed ${dragging ? 'var(--accent-blue)' : 'var(--border)'}`,
                background: dragging ? 'rgba(79,125,255,0.05)' : 'var(--bg-secondary)',
                padding: compact ? '16px' : '32px',
            }}>
            <input id={id} type="file" accept={accept} className="hidden" onChange={onChange} />
            {file ? (
                <p className="text-sm font-semibold" style={{ color: 'var(--accent-blue)' }}>
                    ✓ {file.name} — {(file.size / 1024).toFixed(1)} KB
                </p>
            ) : (
                <>
                    <div className={compact ? 'text-2xl mb-1' : 'text-4xl mb-3'}>{icon}</div>
                    <p className={compact ? 'text-xs' : 'text-sm'} style={{ color: 'var(--text-secondary)' }}>
                        {placeholder}
                    </p>
                </>
            )}
        </div>
    )
}
