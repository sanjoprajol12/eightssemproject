import React, { useState, useEffect } from 'react';
import {
    Sparkles, ShieldCheck, Zap, Trash2, Copy, Download,
    Printer, Link2, ExternalLink, AlertTriangle, CheckCircle,
    XCircle, HelpCircle, Layers, BookOpen, BarChart3, Lock
} from 'lucide-react';

const REAL_WORDS = new Set(['study','research','university','confirmed','official','report','according','spokesperson','announced','data','analysis','published','journal','committee','government','authority','minister','statement','survey','percent','figures','evidence','statistics']);
const FAKE_WORDS = new Set(['shocking','exposed','bombshell','secret','banned','coverup','truth','mainstream','agenda','globalist','radical','hoax','fake','scam','plandemic','crisis','urgent','must','share','deleted','wake','puppets','corrupt','illegal','destroy']);
const WARN_WORDS = new Set(['unbelievable','incredible','devastating','catastrophic','outrage','explosive','terrifying','breaking','exclusive','never','always','everyone','nobody','100%','guaranteed','immediate','final','warning','alert','danger']);

export const Index = ({ onNavigateToLogin, onNavigateToDashboard }) => {
    const [activeTab, setActiveTab] = useState('text');
    const [textInput, setTextInput] = useState('');
    const [urlInput, setUrlInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    // SVG Gauge calculation
    const gaugeTotal = 251.2;
    const confidenceScore = result ? (parseFloat(result.confidence) || 0) : 0;
    const isReal = result?.result === 'Real News';
    const isInconclusive = result?.result === 'Inconclusive';
    const gaugeOffset = gaugeTotal - (confidenceScore / 100) * gaugeTotal;
    const gaugeColor = isReal ? 'var(--real, #10b981)' : isInconclusive ? 'var(--warning, #f59e0b)' : 'var(--fake, #f43f5e)';

    const wordsCount = textInput.trim() ? textInput.trim().split(/\s+/).length : 0;
    const charsCount = textInput.length;

    const handleClear = () => {
        setTextInput('');
        setUrlInput('');
        setResult(null);
        setError('');
    };

    const handleAnalyze = async () => {
        setError('');
        let endpoint = '/detect/';
        let payload = {};

        if (activeTab === 'text') {
            const content = textInput.trim();
            if (!content) {
                setError('Please paste or write an article text to analyze.');
                return;
            }
            payload = { content };
        } else {
            const url = urlInput.trim();
            if (!url) {
                setError('Please provide a valid news article URL.');
                return;
            }
            endpoint = '/detect-url/';
            payload = { url };
        }

        setIsLoading(true);
        setResult(null);

        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (res.ok && !data.error) {
                setResult(data);
            } else {
                setError(data.error || 'Analysis failed. Please check the input.');
            }
        } catch (err) {
            setError('Could not connect to detection engine.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="detector-root">
            <header className="detector-nav">
                <a href="/" className="nav-brand">
                    <span className="logo-icon">🔍</span>
                    <span>TruthLens</span>
                </a>
                <div className="nav-right">
                    <a 
                        href="/login/" 
                        className="btn btn-secondary btn-sm"
                        onClick={(e) => {
                            if (onNavigateToLogin) {
                                e.preventDefault();
                                onNavigateToLogin();
                            }
                        }}
                    >
                        <Lock size={14} />
                        <span>Admin Login</span>
                    </a>
                </div>
            </header>

            <main className="detector-main">
                <section className="hero-section">
                    <div className="hero-badge">
                        <Sparkles size={14} />
                        <span>State-of-the-Art Forensic Verification</span>
                    </div>
                    <h1>Fake News Intelligence Engine</h1>
                    <p className="hero-sub">
                        Analyze news articles, statements, and URLs with dual neural reason extraction, linguistic bias profiling, and semantic cross-referencing.
                    </p>
                </section>

                <div className="analyzer-card">
                    <div className="analyzer-tabs">
                        <button 
                            className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
                            onClick={() => setActiveTab('text')}
                        >
                            Paste Article Text
                        </button>
                        <button 
                            className={`tab-btn ${activeTab === 'url' ? 'active' : ''}`}
                            onClick={() => setActiveTab('url')}
                        >
                            Analyze via URL
                        </button>
                    </div>

                    {error && (
                        <div className="alert alert-error" style={{ margin: '1rem' }}>
                            <AlertTriangle size={16} />
                            <span>{error}</span>
                        </div>
                    )}

                    <div className="analyzer-body">
                        {activeTab === 'text' ? (
                            <div className="textarea-wrap">
                                <textarea
                                    className="main-textarea"
                                    placeholder="Paste full article text, headline, or claim to evaluate authenticity..."
                                    value={textInput}
                                    onChange={(e) => setTextInput(e.target.value)}
                                    rows={8}
                                />
                                <div className="text-meta-bar">
                                    <span>{wordsCount} words • {charsCount} characters</span>
                                    <button className="btn-ghost-sm" onClick={handleClear}>
                                        <Trash2 size={13} />
                                        <span>Clear</span>
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="url-input-wrap" style={{ padding: '1rem' }}>
                                <input
                                    type="url"
                                    className="form-control"
                                    placeholder="https://example.com/news/article-headline"
                                    value={urlInput}
                                    onChange={(e) => setUrlInput(e.target.value)}
                                />
                            </div>
                        )}

                        <div className="analyzer-actions" style={{ padding: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                            <button 
                                className="btn-submit"
                                style={{ maxWidth: '240px' }}
                                onClick={handleAnalyze}
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <div className="spinner" style={{ display: 'block' }}></div>
                                ) : (
                                    <span className="btn-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <Zap size={16} />
                                        <span>Analyze Article</span>
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {result && (
                    <div className="results-container" style={{ marginTop: '2rem' }}>
                        <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                            <div className="verdict-banner" style={{ marginBottom: '1.5rem' }}>
                                <h2 style={{ color: gaugeColor, fontSize: '2rem', fontWeight: 800 }}>
                                    {result.result}
                                </h2>
                                <p style={{ color: 'var(--muted)', fontSize: '0.95rem' }}>
                                    Confidence Rating: {result.confidence}% • Source: {result.source || 'ML Multi-Classifier'}
                                </p>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.5rem' }}>
                                <svg width="120" height="120" viewBox="0 0 100 100">
                                    <circle cx="50" cy="50" r="40" stroke="var(--border)" strokeWidth="8" fill="none" />
                                    <circle
                                        cx="50" cy="50" r="40"
                                        stroke={gaugeColor}
                                        strokeWidth="8"
                                        fill="none"
                                        strokeDasharray={gaugeTotal}
                                        strokeDashoffset={gaugeOffset}
                                        strokeLinecap="round"
                                        transform="rotate(-90 50 50)"
                                        style={{ transition: 'stroke-dashoffset 0.8s ease' }}
                                    />
                                    <text x="50" y="55" textAnchor="middle" fill="currentColor" fontSize="16" fontWeight="bold">
                                        {Math.round(confidenceScore)}%
                                    </text>
                                </svg>
                            </div>

                            {result.reasons && (
                                <div style={{ textAlign: 'left', marginTop: '1.5rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
                                    <h4 style={{ marginBottom: '0.5rem' }}>Key Diagnostic Factors:</h4>
                                    <ul style={{ paddingLeft: '1.25rem', color: 'var(--text)' }}>
                                        {Array.isArray(result.reasons) ? (
                                            result.reasons.map((r, i) => <li key={i}>{r}</li>)
                                        ) : (
                                            <li>{String(result.reasons)}</li>
                                        )}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Index;
