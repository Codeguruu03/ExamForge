import { useState, useCallback } from 'react'
import axios from 'axios'

const ACCEPT_TYPES = '.pdf,.docx,.txt,.csv,.jpg,.jpeg,.png,.tiff,.bmp,.gif'

export default function UploadPage({ onAnalysisComplete }) {
    const [file, setFile] = useState(null)
    const [dragging, setDragging] = useState(false)
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState('')
    const [error, setError] = useState('')

    const handleFile = (f) => {
        setFile(f)
        setError('')
    }

    const onDrop = useCallback((e) => {
        e.preventDefault()
        setDragging(false)
        const f = e.dataTransfer.files[0]
        if (f) handleFile(f)
    }, [])

    const onDragOver = (e) => { e.preventDefault(); setDragging(true) }
    const onDragLeave = () => setDragging(false)

    const handleSubmit = async () => {
        if (!file) return
        setLoading(true)
        setError('')

        try {
            // Step 1: Upload + Normalize
            setStep('📄 Extracting and normalizing questions...')
            const form = new FormData()
            form.append('file', file)
            const { data: normResult } = await axios.post('/api/upload/', form, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            // Step 2: Similarity detection
            setStep('🔍 Detecting duplicate and similar questions...')
            const { data: simResult } = await axios.post('/api/similarity/', {
                exam: normResult.exam
            })

            setStep('✅ Analysis complete!')
            onAnalysisComplete({ normResult, simResult })
        } catch (err) {
            const msg = err.response?.data?.detail || err.message || 'Unknown error'
            setError(msg)
        } finally {
            setLoading(false)
            setStep('')
        }
    }

    return (
        <div className="max-w-2xl mx-auto pt-8">
            {/* Hero */}
            <div className="text-center mb-10">
                <h2 className="text-4xl font-extrabold mb-3"
                    style={{ background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Analyze Your Exam
                </h2>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Upload a PDF, Word document, or image. Get instant quality insights.
                </p>
            </div>

            {/* Drop Zone */}
            <div
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onClick={() => document.getElementById('fileInput').click()}
                className="rounded-2xl p-10 text-center cursor-pointer transition-all duration-200"
                style={{
                    border: `2px dashed ${dragging ? 'var(--accent-blue)' : 'var(--border)'}`,
                    background: dragging ? 'rgba(79,125,255,0.05)' : 'var(--bg-card)',
                    transform: dragging ? 'scale(1.01)' : 'scale(1)',
                }}
            >
                <input id="fileInput" type="file" accept={ACCEPT_TYPES} className="hidden"
                    onChange={(e) => handleFile(e.target.files[0])} />
                <div className="text-5xl mb-4">📂</div>
                {file ? (
                    <>
                        <p className="font-semibold text-lg" style={{ color: 'var(--accent-blue)' }}>
                            ✓ {file.name}
                        </p>
                        <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                            {(file.size / 1024).toFixed(1)} KB — click to change
                        </p>
                    </>
                ) : (
                    <>
                        <p className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                            Drop your exam file here
                        </p>
                        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
                            PDF, DOCX, Images (JPG/PNG) • Max 10MB
                        </p>
                    </>
                )}
            </div>

            {/* Supported formats */}
            <div className="flex gap-2 flex-wrap justify-center mt-4">
                {['PDF', 'DOCX', 'JPG', 'PNG', 'TIFF', 'CSV'].map(fmt => (
                    <span key={fmt} className="text-xs px-2 py-1 rounded"
                        style={{ background: 'var(--bg-card)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
                        {fmt}
                    </span>
                ))}
            </div>

            {/* Status / Error */}
            {loading && (
                <div className="mt-6 p-4 rounded-xl text-center"
                    style={{ background: 'rgba(79,125,255,0.1)', border: '1px solid rgba(79,125,255,0.3)' }}>
                    <div className="animate-pulse text-sm" style={{ color: 'var(--accent-blue)' }}>
                        {step}
                    </div>
                </div>
            )}
            {error && (
                <div className="mt-6 p-4 rounded-xl"
                    style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: 'var(--accent-red)' }}>
                    <p className="font-semibold text-sm">❌ Error</p>
                    <p className="text-sm mt-1 opacity-80">{error}</p>
                </div>
            )}

            {/* Submit button */}
            <button
                onClick={handleSubmit}
                disabled={!file || loading}
                className="w-full mt-6 py-4 rounded-xl font-bold text-lg transition-all duration-200"
                style={{
                    background: file && !loading
                        ? 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))'
                        : 'var(--bg-card)',
                    color: file && !loading ? 'white' : 'var(--text-secondary)',
                    cursor: file && !loading ? 'pointer' : 'not-allowed',
                    border: 'none',
                    opacity: loading ? 0.7 : 1,
                }}
            >
                {loading ? '⏳ Processing...' : '🚀 Analyze Exam'}
            </button>

            {/* Info cards */}
            <div className="grid grid-cols-3 gap-4 mt-10">
                {[
                    { icon: '📃', label: 'OCR + Parsing', desc: 'Extracts questions from any format' },
                    { icon: '📊', label: 'CTT Metrics', desc: 'Difficulty, discrimination, reliability' },
                    { icon: '🔍', label: 'Duplicate Detection', desc: 'TF-IDF similarity analysis' },
                ].map(item => (
                    <div key={item.label} className="p-4 rounded-xl text-center"
                        style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                        <div className="text-2xl mb-2">{item.icon}</div>
                        <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>{item.label}</p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}
