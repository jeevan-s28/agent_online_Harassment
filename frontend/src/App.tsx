import { useState, useEffect } from 'react'
import axios from 'axios'
import { AlertTriangle, CheckCircle, Loader2, ShieldAlert, ShieldCheck } from 'lucide-react'

// Configure API Base URL
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://agent-online-harassment-backend.onrender.com';

axios.defaults.baseURL = API_BASE_URL;

interface ReasoningStep {
    agent: string
    thought: string
    output: string
}

interface AnalysisResult {
    status: 'safe' | 'harmful'
    category: string
    severity: string
    reasoning_chain: ReasoningStep[]
    suggested_action: string
}

function App() {
    const [inputText, setInputText] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<AnalysisResult | null>(null)
    const [history, setHistory] = useState<any[]>([])

    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchHistory()
    }, [])

    const fetchHistory = async () => {
        try {
            const res = await axios.get('/api/history')
            setHistory(res.data)
        } catch (error) {
            console.error("Failed to fetch history", error)
        }
    }

    const handleAnalyze = async () => {
        if (!inputText.trim()) return
        setLoading(true)
        setResult(null)
        setError(null)
        try {
            const res = await axios.post('/api/analyze', { text: inputText })
            setResult(res.data)
            fetchHistory()
        } catch (err: any) {
            console.error("Analysis failed", err)
            if (err.response) {
                if (err.response.status === 500) {
                    setError("⚠️ Server Error (500). Something went wrong on our end. Please try again later.")
                } else if (err.response.status === 401) {
                    setError("⚠️ Unauthorized (401). Please check your API keys or credentials.")
                } else {
                    setError(`⚠️ Error: ${err.response.data.detail || "An unexpected error occurred."}`)
                }
            } else {
                setError("⚠️ Network Error. Please check your connection.")
            }
        } finally {
            setLoading(false)
        }
    }



    const handleHistoryClick = (item: any) => {
        // Map history item to AnalysisResult structure
        const mappedResult: AnalysisResult = {
            status: item.category === 'Safe' || item.category === 'None' ? 'safe' : 'harmful',
            category: item.category,
            severity: item.severity,
            reasoning_chain: item.reasoning_chain,
            suggested_action: item.suggested_action
        }

        setResult(mappedResult)
        setError(null)

        // Populate input
        setInputText(item.content)
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex">
            {/* Sidebar History */}
            <aside className="w-64 bg-slate-900 border-r border-slate-800 p-4 hidden md:block overflow-y-auto h-screen sticky top-0">
                <h2 className="text-xl font-bold mb-4 text-indigo-400">History</h2>
                <div className="space-y-3">
                    {history.map((item) => (
                        <div
                            key={item.id}
                            onClick={() => handleHistoryClick(item)}
                            className="p-3 bg-slate-800 rounded-lg text-sm hover:bg-slate-700 transition cursor-pointer border border-transparent hover:border-indigo-500/30"
                        >
                            <p className="font-medium truncate text-slate-200">{item.content}</p>
                            <div className="flex justify-between mt-2 text-xs text-slate-400">
                                <span className={`px-1.5 py-0.5 rounded ${item.category === 'Safe' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                                    {item.category}
                                </span>
                                <span title={item.source}>{item.source === 'Instagram' ? '📸' : '✍️'}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 max-w-5xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
                        Agentic Harassment Detection
                    </h1>
                    <p className="text-slate-400 mt-2">Multi-Agent System</p>
                </header>

                {/* Input Area */}
                <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-lg mb-8">
                    <textarea
                        className="w-full bg-slate-950 border border-slate-700 rounded-lg p-4 text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition h-32 resize-none"
                        placeholder="Paste text here to analyze..."
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                    />
                    <div className="flex justify-end mt-4">
                        <button
                            onClick={handleAnalyze}
                            disabled={loading || !inputText}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="animate-spin w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
                            {loading ? 'Analyzing...' : 'Analyze Text'}
                        </button>
                    </div>
                    {error && (
                        <div className="mt-4 p-3 rounded-lg text-sm bg-red-900/20 text-red-400 border border-red-900/50">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Dashboard */}
                {result && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

                        {/* Verdict Card */}
                        <div className="lg:col-span-1 space-y-6">
                            <div className={`p-6 rounded-xl border ${result.status === 'safe' ? 'bg-green-900/20 border-green-800' : 'bg-red-900/20 border-red-800'}`}>
                                <div className="flex items-center gap-3 mb-4">
                                    {result.status === 'safe' ? (
                                        <CheckCircle className="w-8 h-8 text-green-500" />
                                    ) : (
                                        <AlertTriangle className="w-8 h-8 text-red-500" />
                                    )}
                                    <div>
                                        <h3 className="text-lg font-bold uppercase tracking-wider">{result.status}</h3>
                                        <p className="text-sm text-slate-400">Final Verdict</p>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div className="flex justify-between items-center p-2 bg-slate-950/50 rounded">
                                        <span className="text-slate-400 text-sm">Category</span>
                                        <span className="font-medium">{result.category}</span>
                                    </div>
                                    <div className="flex justify-between items-center p-2 bg-slate-950/50 rounded">
                                        <span className="text-slate-400 text-sm">Severity</span>
                                        <span className={`font-bold px-2 py-0.5 rounded text-xs ${result.severity === 'High' || result.severity === 'Critical' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                                            }`}>
                                            {result.severity}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center p-2 bg-slate-950/50 rounded">
                                        <span className="text-slate-400 text-sm">Action</span>
                                        <span className="font-medium text-indigo-400">{result.suggested_action}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Reasoning Chain */}
                        <div className="lg:col-span-2">
                            <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                                <div className="p-4 border-b border-slate-800 bg-slate-900/50">
                                    <h3 className="font-bold flex items-center gap-2">
                                        <ShieldAlert className="w-4 h-4 text-indigo-400" />
                                        Agent Reasoning Chain
                                    </h3>
                                </div>
                                <div className="divide-y divide-slate-800">
                                    {result.reasoning_chain.map((step, idx) => (
                                        <div key={idx} className="p-4 hover:bg-slate-800/50 transition">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 bg-indigo-950/30 px-2 py-1 rounded">
                                                    {step.agent}
                                                </span>
                                            </div>
                                            <div className="mb-2">
                                                <p className="text-sm text-slate-300 italic">" {step.thought} "</p>
                                            </div>
                                            <div className="bg-slate-950 p-3 rounded border border-slate-800 text-sm font-mono text-slate-400">
                                                {step.output}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                    </div>
                )}
            </main>
        </div>
    )
}

export default App
