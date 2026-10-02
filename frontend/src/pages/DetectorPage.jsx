import React, { useState, useEffect, useRef } from 'react';
import {
    Sparkles, ShieldCheck, Zap, Trash2, Copy, Download,
    Printer, Link2, ExternalLink, AlertTriangle, CheckCircle,
    XCircle, HelpCircle, Layers, BookOpen, BarChart3, Lock
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { ThemeSwitcher } from '../components/common/ThemeSwitcher';
import { useToast } from '../components/common/Toast';

const REAL_WORDS = new Set(['study','research','university','confirmed','official','report','according','spokesperson','announced','data','analysis','published','journal','committee','government','authority','minister','statement','survey','percent','figures','evidence','statistics']);
const FAKE_WORDS = new Set(['shocking','exposed','bombshell','secret','banned','coverup','truth','mainstream','agenda','globalist','radical','hoax','fake','scam','plandemic','crisis','urgent','must','share','deleted','wake','puppets','corrupt','illegal','destroy']);
const WARN_WORDS = new Set(['unbelievable','incredible','devastating','catastrophic','outrage','explosive','terrifying','breaking','exclusive','never','always','everyone','nobody','100%','guaranteed','immediate','final','warning','alert','danger']);

export const DetectorPage = ({ onNavigate }) => {
    const { showToast } = useToast();
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
    const gaugeColor = isReal ? 'var(--success)' : isInconclusive ? 'var(--warning)' : 'var(--danger)';

    // Word & Char counts
    const wordsCount = textInput.trim() ? textInput.trim().split(/\s+/).length : 0;
    const charsCount = textInput.length;

    // Handle Ctrl + Enter
    const handleKeyDown = (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            handleAnalyze();
        }
    };

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
                setError('Please enter an article URL to analyze.');
                return;
            }
            endpoint = '/api/detect/url/';
            payload = { url };
        }

        setIsLoading(true);
        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.message || data.error || 'Credibility detection failed.');
            }
            setResult(data);
        } catch (err) {
            setError(err.message || 'Network error connecting to AI detection pipeline.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCopyJson = () => {
        if (!result) return;
        navigator.clipboard.writeText(JSON.stringify(result, null, 2));
        showToast('JSON report copied to clipboard!', 'success');
    };

    const handleDownloadJson = () => {
        if (!result) return;
        const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `truthlens-detection-${Date.now()}.json`;
        link.click();
        URL.revokeObjectURL(url);
        showToast('JSON report downloaded!', 'success');
    };

    const handleCopyLink = () => {
        if (!result) return;
        const summary = `TruthLens Verdict: ${result.result} (${confidenceScore.toFixed(1)}%)\n${result.ai_summary || ''}`;
        navigator.clipboard.writeText(summary);
        showToast('Verdict summary copied to clipboard!', 'success');
    };

    const renderHeatmap = (text) => {
        if (!text) return null;
        const words = text.replace(/\n/g, ' ').split(/\s+/).slice(0, 140);
        return words.map((w, idx) => {
            const clean = w.toLowerCase().replace(/[^a-z0-9]/g, '');
            if (REAL_WORDS.has(clean)) return <span key={idx} className="hw-real">{w} </span>;
            if (FAKE_WORDS.has(clean)) return <span key={idx} className="hw-fake">{w} </span>;
            if (WARN_WORDS.has(clean)) return <span key={idx} className="hw-warn">{w} </span>;
            return <span key={idx}>{w} </span>;
        });
    };

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Top Navigation */}
            <nav style={{
                height: 'var(--header-height)',
                backgroundColor: 'var(--bg-header)',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 2rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                    <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 700
                    }}>
                        🔍
                    </div>
                    <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 700 }}>
                        TruthLens
                    </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <ThemeSwitcher />
                    <Button variant="secondary" size="sm" onClick={() => onNavigate('dashboard')} icon={BarChart3}>
                        Dashboard
                    </Button>
                    <Button variant="primary" size="sm" onClick={() => onNavigate('login')} icon={Lock}>
                        Admin Login
                    </Button>
                </div>
            </nav>

            {/* Hero */}
            <div className="detector-hero">
                <div className="status-chip">
                    <span className="pulse" />
                    <span>Ensemble ML Engine Active</span>
                </div>
                <h1 className="detector-title">
                    Detect <em>Fake News</em> with AI Precision
                </h1>
                <p className="detector-subtitle">
                    Paste a headline or article text. Our ensemble pipeline uses FTS5 evidence matching,
                    domain reputation scoring, and multiple ML classifiers to return a credibility verdict in seconds.
                </p>
            </div>

            {/* Main Detector Card */}
            <div className="detector-container">
                <div className="glass-card">
                    {/* Tabs */}
                    <div className="detector-tabs">
                        <button
                            className={`detector-tab-btn ${activeTab === 'text' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('text'); setResult(null); }}
                        >
                            <BookOpen size={16} />
                            <span>Article Text</span>
                        </button>
                        <button
                            className={`detector-tab-btn ${activeTab === 'url' ? 'active' : ''}`}
                            onClick={() => { setActiveTab('url'); setResult(null); }}
                        >
                            <Link2 size={16} />
                            <span>Article URL</span>
                        </button>
                    </div>

                    {/* Inputs */}
                    {activeTab === 'text' ? (
                        <div>
                            <div className="form-group" style={{ marginBottom: '0.5rem' }}>
                                <label className="form-label">News headline or article body</label>
                                <textarea
                                    className="form-textarea"
                                    rows={5}
                                    placeholder="e.g. The Federal Reserve announced interest rate adjustments following quarterly economic review..."
                                    value={textInput}
                                    onChange={(e) => setTextInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                />
                            </div>
                            <div className="input-meta-row">
                                <span>{wordsCount} words • {charsCount} characters</span>
                                <span style={{ fontStyle: 'italic' }}>Supports full news articles or short claims</span>
                            </div>

                            {/* Samples */}
                            <div className="examples-wrap">
                                <div className="examples-lbl">Try These Examples</div>
                                <div className="chips-list">
                                    <button
                                        className="sample-chip"
                                        onClick={() => setTextInput('The US Department of Labor reported that nonfarm payrolls increased by 175,000, while the unemployment rate remained at 3.9%.')}
                                    >
                                        <span className="chip-tag" style={{ color: 'var(--success)', background: 'var(--success-dim)' }}>Gov</span>
                                        <span>📉 Unemployment decline</span>
                                    </button>
                                    <button
                                        className="sample-chip"
                                        onClick={() => setTextInput('Scientists in Antarctica uncover living colony of velociraptors thriving in secret thermal cave.')}
                                    >
                                        <span className="chip-tag" style={{ color: 'var(--danger)', background: 'var(--danger-dim)' }}>Hoax</span>
                                        <span>🦖 Dinosaur colony</span>
                                    </button>
                                    <button
                                        className="sample-chip"
                                        onClick={() => setTextInput('The Federal Reserve announced a 25 basis point rate cut following the FOMC meeting.')}
                                    >
                                        <span className="chip-tag" style={{ color: 'var(--secondary)', background: 'var(--secondary-dim)' }}>Finance</span>
                                        <span>🏛️ Fed rate decision</span>
                                    </button>
                                    <button
                                        className="sample-chip"
                                        onClick={() => setTextInput('New research proves that drinking bleach cures all known infectious diseases immediately.')}
                                    >
                                        <span className="chip-tag" style={{ color: 'var(--warning)', background: 'var(--warning-dim)' }}>Health</span>
                                        <span>⚠️ Bleach cure claim</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ marginBottom: '1.25rem' }}>
                            <div className="form-group">
                                <label className="form-label">Article Web URL</label>
                                <input
                                    type="url"
                                    className="form-control"
                                    placeholder="https://reuters.com/article/example-headline..."
                                    value={urlInput}
                                    onChange={(e) => setUrlInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                />
                            </div>
                            <div className="input-meta-row">
                                <span>Content is safely scraped and domain reputation is factored into credibility analysis.</span>
                            </div>
                        </div>
                    )}

                    {/* Action buttons */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem' }}>
                        <Button variant="ghost" icon={Trash2} onClick={handleClear}>
                            Clear
                        </Button>
                        <Button
                            variant="primary"
                            icon={Zap}
                            onClick={handleAnalyze}
                            isLoading={isLoading}
                        >
                            <span>Analyze Credibility</span>
                            <span style={{ fontSize: '0.72rem', opacity: 0.8, background: 'rgba(0,0,0,0.25)', padding: '0.15rem 0.4rem', borderRadius: '4px', marginLeft: '0.35rem' }}>
                                Ctrl + ↵
                            </span>
                        </Button>
                    </div>

                    {/* Error Box */}
                    {error && (
                        <div style={{
                            marginTop: '1.25rem',
                            padding: '0.9rem 1.25rem',
                            backgroundColor: 'var(--danger-dim)',
                            border: '1px solid var(--danger-border)',
                            color: 'var(--danger)',
                            borderRadius: 'var(--radius-md)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.6rem'
                        }}>
                            <AlertTriangle size={18} />
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Results Presentation */}
                    {result && (
                        <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem' }}>
                            {/* Actions toolbar */}
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
                                <Button variant="secondary" size="sm" icon={Link2} onClick={handleCopyLink}>
                                    Copy Link
                                </Button>
                                <Button variant="secondary" size="sm" icon={Printer} onClick={() => window.print()}>
                                    Print / PDF
                                </Button>
                                <Button variant="secondary" size="sm" icon={Copy} onClick={handleCopyJson}>
                                    Copy JSON
                                </Button>
                                <Button variant="secondary" size="sm" icon={Download} onClick={handleDownloadJson}>
                                    Download JSON
                                </Button>
                            </div>

                            {/* Human Review Banner */}
                            {result.review_needed && (
                                <div style={{
                                    backgroundColor: 'var(--warning-dim)',
                                    border: '1px solid var(--warning-border)',
                                    borderRadius: 'var(--radius-md)',
                                    padding: '0.85rem 1.25rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.75rem',
                                    marginBottom: '1.25rem'
                                }}>
                                    <AlertTriangle size={20} style={{ color: 'var(--warning)', flexShrink: 0 }} />
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                                        <strong>Human Review Recommended:</strong> Confidence is in the borderline range.
                                        This detection has been flagged for expert verification in the review queue.
                                    </div>
                                </div>
                            )}

                            {/* SVG Radial Confidence Gauge */}
                            <div className="gauge-wrap">
                                <svg className="gauge-svg" viewBox="0 0 200 110">
                                    <path className="gauge-bg" d="M 20 100 A 80 80 0 0 1 180 100" />
                                    <path
                                        className="gauge-arc"
                                        d="M 20 100 A 80 80 0 0 1 180 100"
                                        strokeDasharray={gaugeTotal}
                                        strokeDashoffset={gaugeOffset}
                                        stroke={gaugeColor}
                                    />
                                    <text className="gauge-label" x="100" y="90" style={{ fill: gaugeColor }}>
                                        {confidenceScore.toFixed(0)}%
                                    </text>
                                    <text className="gauge-sub" x="100" y="106">
                                        CREDIBILITY SCORE
                                    </text>
                                </svg>
                                <div style={{ display: 'flex', justifyContent: 'space-between', width: '180px', marginTop: '-4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                    <span>0% Fake</span>
                                    <span>100% Real</span>
                                </div>
                            </div>

                            {/* Verdict Banner */}
                            <div className={`verdict-banner ${isReal ? 'real' : isInconclusive ? 'uncertain' : 'fake'}`}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    {isReal ? <CheckCircle size={32} style={{ color: 'var(--success)' }} /> :
                                     isInconclusive ? <HelpCircle size={32} style={{ color: 'var(--warning)' }} /> :
                                     <XCircle size={32} style={{ color: 'var(--danger)' }} />}
                                    <div>
                                        <div className="verdict-title">
                                            {result.result || 'Credibility Analysis Complete'}
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                            Source: {result.source || 'Ensemble Pipeline'} • Latency: {result.latency_ms || 42}ms
                                        </div>
                                    </div>
                                </div>
                                <Badge variant={isReal ? 'success' : isInconclusive ? 'warning' : 'danger'}>
                                    {confidenceScore.toFixed(1)}% Confidence
                                </Badge>
                            </div>

                            {/* AI Executive Analysis */}
                            {result.ai_summary && (
                                <div style={{
                                    backgroundColor: 'var(--primary-dim)',
                                    border: '1px solid var(--border-focus)',
                                    borderRadius: 'var(--radius-md)',
                                    padding: '1rem 1.25rem',
                                    marginBottom: '1.25rem'
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                                        <Sparkles size={16} />
                                        <span>AI Fact-Checking Summary</span>
                                    </div>
                                    <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                                        {result.ai_summary}
                                    </p>
                                </div>
                            )}

                            {/* Dual Reasons Grid */}
                            {(result.reasons_real?.length > 0 || result.reasons_fake?.length > 0) && (
                                <div className="reasons-grid">
                                    <div className="reason-box real">
                                        <div className="reason-title">
                                            <CheckCircle size={16} />
                                            <span>Signals Supporting Credibility</span>
                                        </div>
                                        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.825rem' }}>
                                            {(result.reasons_real || []).map((r, i) => (
                                                <li key={i} style={{ display: 'flex', gap: '0.4rem' }}>
                                                    <span style={{ color: 'var(--success)' }}>•</span>
                                                    <span>{r}</span>
                                                </li>
                                            ))}
                                            {(!result.reasons_real || result.reasons_real.length === 0) && (
                                                <li style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No positive signals identified</li>
                                            )}
                                        </ul>
                                    </div>

                                    <div className="reason-box fake">
                                        <div className="reason-title">
                                            <AlertTriangle size={16} />
                                            <span>Deceptive / Sensational Flags</span>
                                        </div>
                                        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.825rem' }}>
                                            {(result.reasons_fake || []).map((r, i) => (
                                                <li key={i} style={{ display: 'flex', gap: '0.4rem' }}>
                                                    <span style={{ color: 'var(--danger)' }}>•</span>
                                                    <span>{r}</span>
                                                </li>
                                            ))}
                                            {(!result.reasons_fake || result.reasons_fake.length === 0) && (
                                                <li style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No deceptive flags identified</li>
                                            )}
                                        </ul>
                                    </div>
                                </div>
                            )}

                            {/* Contextual Lexicon Heatmap */}
                            <div className="heatmap-card">
                                <div style={{ fontSize: '0.825rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
                                    Contextual Credibility Lexicon Heatmap
                                </div>
                                <div className="heatmap-legend">
                                    <span><strong style={{ color: 'var(--success)' }}>■</strong> Factual / Evidence</span>
                                    <span><strong style={{ color: 'var(--danger)' }}>■</strong> Deceptive Trigger</span>
                                    <span><strong style={{ color: 'var(--warning)' }}>■</strong> Sensational Tone</span>
                                </div>
                                <div className="heatmap-body">
                                    {renderHeatmap(textInput || result.statement || result.url || '')}
                                </div>
                            </div>

                            {/* Political Bias Meter */}
                            {result.bias && (
                                <div className="bias-card">
                                    <div className="bias-header">
                                        <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#fbbf24' }}>
                                            Political Lean & Bias Radar
                                        </span>
                                        <span className="bias-lean-badge" style={{
                                            backgroundColor: 'rgba(245, 158, 11, 0.2)',
                                            color: '#fbbf24',
                                            border: '1px solid rgba(245, 158, 11, 0.4)'
                                        }}>
                                            {result.bias.political_lean || 'Center / Neutral'}
                                        </span>
                                    </div>
                                    <div className="bias-score-bar">
                                        <div className="bias-score-fill" style={{ width: `${result.bias.bias_score || 25}%` }} />
                                    </div>
                                    <div className="bias-tags">
                                        {(result.bias.bias_types || ['Objective Reporting']).map((t, idx) => (
                                            <span key={idx} className="bias-tag-item">{t}</span>
                                        ))}
                                    </div>
                                    {result.bias.bias_summary && (
                                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.4rem' }}>
                                            {result.bias.bias_summary}
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Model Breakdown */}
                            {result.models && Object.keys(result.models).length > 0 && (
                                <div style={{ marginTop: '1.25rem' }}>
                                    <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                                        Ensemble Classifier Breakdown
                                    </h4>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                                        {Object.entries(result.models).map(([name, m]) => (
                                            <div key={name} style={{
                                                backgroundColor: 'var(--bg-surface)',
                                                border: '1px solid var(--border-subtle)',
                                                borderRadius: 'var(--radius-md)',
                                                padding: '0.75rem 1rem',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'space-between'
                                            }}>
                                                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{name}</span>
                                                <Badge variant={m.prediction === 'Real News' ? 'success' : 'danger'}>
                                                    {m.confidence ? `${(m.confidence * 100).toFixed(0)}%` : m.prediction}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Evidence Matches */}
                            {result.evidence_matches?.length > 0 && (
                                <div style={{ marginTop: '1.5rem' }}>
                                    <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                                        FTS5 Evidence Matches ({result.evidence_matches.length})
                                    </h4>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        {result.evidence_matches.map((ev, i) => (
                                            <div key={i} style={{
                                                backgroundColor: 'var(--bg-surface)',
                                                border: '1px solid var(--border-subtle)',
                                                borderRadius: 'var(--radius-sm)',
                                                padding: '0.75rem 1rem',
                                                fontSize: '0.85rem',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                gap: '1rem'
                                            }}>
                                                <span>{ev.statement || ev.text || ev.title}</span>
                                                <Badge variant="secondary" dot={false}>
                                                    Score: {typeof ev.score === 'number' ? ev.score.toFixed(2) : 'Match'}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
