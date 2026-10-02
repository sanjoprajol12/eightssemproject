import React, { useState, useRef } from 'react';
import {
    Sparkles, ShieldCheck, Zap, Trash2, Copy, Download,
    Printer, Link2, ExternalLink, AlertTriangle, CheckCircle,
    XCircle, HelpCircle, Layers, BookOpen, Home, Info, Mail,
    Send, Phone, User, MessageSquare, Database, Cpu, CheckCircle2
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
    const [currentNav, setCurrentNav] = useState('home'); // 'home' | 'about'
    const [activeTab, setActiveTab] = useState('text');
    const [textInput, setTextInput] = useState('');
    const [urlInput, setUrlInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    // Contact Us Form State
    const [contactForm, setContactForm] = useState({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
    });
    const [isSubmittingEnquiry, setIsSubmittingEnquiry] = useState(false);
    const [enquirySuccess, setEnquirySuccess] = useState(false);
    const [enquiryError, setEnquiryError] = useState('');

    const aboutSectionRef = useRef(null);
    const detectorSectionRef = useRef(null);

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

    // Contact Us Form Submission
    const handleContactSubmit = async (e) => {
        e.preventDefault();
        setEnquiryError('');
        setEnquirySuccess(false);

        if (!contactForm.name.trim() || !contactForm.email.trim() || !contactForm.message.trim()) {
            setEnquiryError('Please provide your name, email address, and message.');
            return;
        }

        setIsSubmittingEnquiry(true);
        try {
            const res = await fetch('/api/v1/cms/enquiries/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: contactForm.name.trim(),
                    email: contactForm.email.trim(),
                    phone: contactForm.phone.trim(),
                    subject: contactForm.subject.trim() || 'General Inquiry',
                    message: contactForm.message.trim(),
                })
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.message || data.detail || 'Failed to submit enquiry.');
            }
            setEnquirySuccess(true);
            setContactForm({ name: '', email: '', phone: '', subject: '', message: '' });
            showToast('Your contact enquiry has been received! We will follow up shortly.', 'success');
        } catch (err) {
            setEnquiryError(err.message || 'Error submitting contact enquiry. Please try again.');
            showToast(err.message || 'Error submitting contact enquiry', 'error');
        } finally {
            setIsSubmittingEnquiry(false);
        }
    };

    const scrollToHome = () => {
        setCurrentNav('home');
        if (detectorSectionRef.current) {
            detectorSectionRef.current.scrollIntoView({ behavior: 'smooth' });
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const scrollToAbout = () => {
        setCurrentNav('about');
        if (aboutSectionRef.current) {
            aboutSectionRef.current.scrollIntoView({ behavior: 'smooth' });
        }
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
                padding: '0 2rem',
                position: 'sticky',
                top: 0,
                zIndex: 100,
                backdropFilter: 'blur(12px)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }} onClick={scrollToHome}>
                    <div style={{
                        width: '34px',
                        height: '34px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 700,
                        boxShadow: '0 2px 8px rgba(99, 102, 241, 0.35)'
                    }}>
                        🔍
                    </div>
                    <span style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                        TruthLens
                    </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <button
                            onClick={scrollToHome}
                            style={{
                                background: currentNav === 'home' ? 'var(--primary-dim)' : 'transparent',
                                border: currentNav === 'home' ? '1px solid var(--primary-border)' : '1px solid transparent',
                                color: currentNav === 'home' ? 'var(--primary)' : 'var(--text-secondary)',
                                padding: '0.45rem 0.9rem',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.9rem',
                                fontWeight: 600,
                                cursor: 'pointer',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.45rem',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            <Home size={16} />
                            <span>Home</span>
                        </button>
                        <button
                            onClick={scrollToAbout}
                            style={{
                                background: currentNav === 'about' ? 'var(--primary-dim)' : 'transparent',
                                border: currentNav === 'about' ? '1px solid var(--primary-border)' : '1px solid transparent',
                                color: currentNav === 'about' ? 'var(--primary)' : 'var(--text-secondary)',
                                padding: '0.45rem 0.9rem',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.9rem',
                                fontWeight: 600,
                                cursor: 'pointer',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.45rem',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            <Info size={16} />
                            <span>About</span>
                        </button>
                    </div>

                    <div style={{ height: '24px', width: '1px', backgroundColor: 'var(--border-subtle)' }} />
                    <ThemeSwitcher />
                </div>
            </nav>

            {/* Main Detector Section */}
            <div ref={detectorSectionRef}>
                {/* Hero */}
                <div className="detector-hero">
                    <div className="status-chip">
                        <span className="pulse" />
                        <span>Ensemble ML Engine Active &bull; 14,000+ Ground-Truth Records</span>
                    </div>
                    <h1 className="detector-title">
                        Detect <em>Fake News</em> with AI Precision
                    </h1>
                    <p className="detector-subtitle">
                        Paste a headline or article text. Our ensemble pipeline uses SQLite FTS5 evidence matching,
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
                                    <span style={{ fontStyle: 'italic' }}>Trained on ground-truth benchmark datasets</span>
                                </div>

                                {/* Dataset Samples */}
                                <div className="examples-wrap">
                                    <div className="examples-lbl">Try Ground-Truth Dataset Examples</div>
                                    <div className="chips-list">
                                        <button
                                            className="sample-chip"
                                            onClick={() => setTextInput('When did the decline of coal start? It started when natural gas took off that started to begin in (President George W.) Bushs administration.')}
                                        >
                                            <span className="chip-tag" style={{ color: 'var(--success)', background: 'var(--success-dim)' }}>Real (Dataset)</span>
                                            <span>📉 Coal decline &amp; gas</span>
                                        </button>
                                        <button
                                            className="sample-chip"
                                            onClick={() => setTextInput('Says the Annies List political group supports third-trimester abortions on demand.')}
                                        >
                                            <span className="chip-tag" style={{ color: 'var(--danger)', background: 'var(--danger-dim)' }}>Fake (Dataset)</span>
                                            <span>⚠️ Third-trimester claim</span>
                                        </button>
                                        <button
                                            className="sample-chip"
                                            onClick={() => setTextInput('The Federal Reserve announced interest rate adjustments following quarterly economic review.')}
                                        >
                                            <span className="chip-tag" style={{ color: 'var(--secondary)', background: 'var(--secondary-dim)' }}>Finance</span>
                                            <span>🏛️ Fed rate decision</span>
                                        </button>
                                        <button
                                            className="sample-chip"
                                            onClick={() => setTextInput('Scientists in Antarctica uncover living colony of velociraptors thriving in secret thermal cave.')}
                                        >
                                            <span className="chip-tag" style={{ color: 'var(--warning)', background: 'var(--warning-dim)' }}>Hoax</span>
                                            <span>🦖 Dinosaur colony</span>
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
                                    <span>Content is safely extracted and domain credibility reputation is factored into analysis.</span>
                                </div>
                            </div>
                        )}

                        {/* Error Alert */}
                        {error && (
                            <div className="alert alert-danger" style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <AlertTriangle size={18} />
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Action Toolbar */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
                            <Button variant="ghost" size="sm" onClick={handleClear} icon={Trash2}>
                                Clear
                            </Button>
                            <Button
                                variant="primary"
                                onClick={handleAnalyze}
                                disabled={isLoading}
                                icon={Sparkles}
                            >
                                {isLoading ? 'Analyzing Credibility...' : 'Analyze Credibility (Ctrl + ↵)'}
                            </Button>
                        </div>

                        {/* Results Box */}
                        {result && (
                            <div style={{ marginTop: '2.5rem', paddingTop: '2rem', borderTop: '1px solid var(--border-subtle)' }}>
                                <div style={{
                                    backgroundColor: isReal ? 'rgba(16, 185, 129, 0.08)' : isInconclusive ? 'rgba(245, 158, 11, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                                    border: `1px solid ${gaugeColor}`,
                                    borderRadius: 'var(--radius-lg)',
                                    padding: '1.75rem',
                                    marginBottom: '1.5rem'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                            {isReal ? (
                                                <CheckCircle size={32} color="var(--success)" />
                                            ) : isInconclusive ? (
                                                <HelpCircle size={32} color="var(--warning)" />
                                            ) : (
                                                <XCircle size={32} color="var(--danger)" />
                                            )}
                                            <div>
                                                <h3 style={{ fontSize: '1.5rem', fontWeight: 800, margin: 0, color: gaugeColor }}>
                                                    {result.result}
                                                </h3>
                                                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                                    Source: {result.source || 'Ensemble Pipeline'}
                                                </span>
                                            </div>
                                        </div>

                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: gaugeColor }}>
                                                {confidenceScore.toFixed(1)}%
                                            </div>
                                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                                Confidence Score
                                            </span>
                                        </div>
                                    </div>

                                    {/* Action Chips */}
                                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem', flexWrap: 'wrap' }}>
                                        <Button variant="secondary" size="sm" onClick={handleCopyJson} icon={Copy}>
                                            Copy JSON
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={handleDownloadJson} icon={Download}>
                                            Download Report
                                        </Button>
                                        <Button variant="secondary" size="sm" onClick={handleCopyLink} icon={Link2}>
                                            Copy Verdict Summary
                                        </Button>
                                    </div>
                                </div>

                                {/* AI Reasoning & Explainability */}
                                {result.ai_summary && (
                                    <div style={{
                                        backgroundColor: 'var(--bg-surface)',
                                        border: '1px solid var(--border-subtle)',
                                        borderRadius: 'var(--radius-md)',
                                        padding: '1.25rem',
                                        marginBottom: '1.25rem'
                                    }}>
                                        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                            <Zap size={16} color="var(--primary)" />
                                            <span>Executive Intelligence Brief</span>
                                        </h4>
                                        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                                            {result.ai_summary}
                                        </p>
                                    </div>
                                )}

                                {/* Token Heatmap */}
                                {textInput && (
                                    <div style={{
                                        backgroundColor: 'var(--bg-surface)',
                                        border: '1px solid var(--border-subtle)',
                                        borderRadius: 'var(--radius-md)',
                                        padding: '1.25rem',
                                        marginBottom: '1.25rem'
                                    }}>
                                        <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                                            Lexical Signal Highlighting
                                        </h4>
                                        <div style={{ fontSize: '0.95rem', lineHeight: 1.8 }}>
                                            {renderHeatmap(textInput)}
                                        </div>
                                        <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                                                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--success)' }} />
                                                Credible Tokens
                                            </span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                                                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: 'var(--danger)' }} />
                                                Suspicious / Clickbait
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {/* Model Breakdown */}
                                {result.models && result.models.predictions && Object.keys(result.models.predictions).length > 0 && (
                                    <div style={{ marginTop: '1.25rem' }}>
                                        <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                                            Ensemble Classifier Breakdown
                                        </h4>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                                            {Object.entries(result.models.predictions).map(([name, pred]) => {
                                                const prob = result.models.probabilities?.[name];
                                                const isPredReal = pred === 1 || pred === true;
                                                return (
                                                    <div key={name} style={{
                                                        backgroundColor: 'var(--bg-surface)',
                                                        border: '1px solid var(--border-subtle)',
                                                        borderRadius: 'var(--radius-md)',
                                                        padding: '0.75rem 1rem',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'space-between'
                                                    }}>
                                                        <span style={{ fontSize: '0.85rem', fontWeight: 600, textTransform: 'capitalize' }}>
                                                            {name.replace(/_/g, ' ')}
                                                        </span>
                                                        <Badge variant={isPredReal ? 'success' : 'danger'}>
                                                            {isPredReal ? 'Real' : 'Fake'} {prob ? `(${Math.round(prob * 100)}%)` : ''}
                                                        </Badge>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* About & Contact Us Section */}
            <div
                ref={aboutSectionRef}
                style={{
                    backgroundColor: 'var(--bg-surface)',
                    borderTop: '1px solid var(--border-subtle)',
                    padding: '4rem 1.5rem',
                    marginTop: 'auto'
                }}
            >
                <div style={{ maxWidth: '1040px', margin: '0 auto' }}>
                    {/* About Header */}
                    <div style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
                        <div className="status-chip" style={{ background: 'var(--primary-dim)', color: 'var(--primary)', borderColor: 'var(--primary-border)' }}>
                            <Info size={14} />
                            <span>Platform Overview &bull; Forensic Architecture</span>
                        </div>
                        <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '2.4rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '1rem' }}>
                            About TruthLens AI &amp; Our Mission
                        </h2>
                        <p style={{ color: 'var(--text-secondary)', maxWidth: '680px', margin: '0 auto', fontSize: '1.05rem', lineHeight: 1.7 }}>
                            TruthLens is an enterprise automated disinformation forensics engine engineered to combat fabricated news, hyperpartisan clickbait, and manipulated digital journalism.
                        </p>
                    </div>

                    {/* 3 Pillars Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '4rem' }}>
                        <div style={{
                            backgroundColor: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-lg)',
                            padding: '1.75rem'
                        }}>
                            <div style={{
                                width: '42px',
                                height: '42px',
                                borderRadius: 'var(--radius-md)',
                                background: 'var(--primary-dim)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'var(--primary)',
                                marginBottom: '1.25rem'
                            }}>
                                <Database size={22} />
                            </div>
                            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.65rem' }}>
                                Ground-Truth Corpus Indexing
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                                High-speed SQLite FTS5 BM25 search combined with SHA-256 cryptographic content hashes checks statements against over 28,000 ground-truth records from the LIAR benchmark and verified journalistic archives.
                            </p>
                        </div>

                        <div style={{
                            backgroundColor: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-lg)',
                            padding: '1.75rem'
                        }}>
                            <div style={{
                                width: '42px',
                                height: '42px',
                                borderRadius: 'var(--radius-md)',
                                background: 'var(--secondary-dim)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'var(--secondary)',
                                marginBottom: '1.25rem'
                            }}>
                                <Cpu size={22} />
                            </div>
                            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.65rem' }}>
                                Multi-Classifier ML Ensemble
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                                Integrates TF-IDF N-grams (1-4 grams) across Logistic Regression, Naive Bayes, Linear Support Vector Machines, Random Forests, and online SGD classifiers for unbiased probabilistic consensus.
                            </p>
                        </div>

                        <div style={{
                            backgroundColor: 'var(--bg-card)',
                            border: '1px solid var(--border-subtle)',
                            borderRadius: 'var(--radius-lg)',
                            padding: '1.75rem'
                        }}>
                            <div style={{
                                width: '42px',
                                height: '42px',
                                borderRadius: 'var(--radius-md)',
                                background: 'var(--success-dim)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'var(--success)',
                                marginBottom: '1.25rem'
                            }}>
                                <ShieldCheck size={22} />
                            </div>
                            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.65rem' }}>
                                Deep Explainability &amp; XAI
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                                Generates granular token heatmaps, objectivity scoring, sensationalism indices, and narrative summaries so users understand exactly why a headline was rated credible or deceptive.
                            </p>
                        </div>
                    </div>

                    {/* Contact Us Section */}
                    <div style={{
                        backgroundColor: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-lg)',
                        padding: '2.5rem',
                        boxShadow: '0 20px 40px -15px rgba(0,0,0,0.3)'
                    }}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2.5rem' }}>
                            {/* Contact Intro */}
                            <div>
                                <div className="status-chip" style={{ background: 'var(--primary-dim)', color: 'var(--primary)', borderColor: 'var(--primary-border)', marginBottom: '1rem' }}>
                                    <Mail size={14} />
                                    <span>Editorial Integrity &bull; Contact Enquiries</span>
                                </div>
                                <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.85rem', fontWeight: 800, marginBottom: '1rem' }}>
                                    Get in Touch with Our Team
                                </h3>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.7, marginBottom: '2rem' }}>
                                    Notice an inaccurate verdict, have questions about dataset indexing, or wish to integrate TruthLens with your newsroom? Submit an inquiry and our team will respond promptly.
                                </p>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <Mail size={16} />
                                        </div>
                                        <span>contact@facknews.local</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <Phone size={16} />
                                        </div>
                                        <span>+977 (01) 456-7890</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <ShieldCheck size={16} />
                                        </div>
                                        <span>Submissions saved directly to Contact Enquiries</span>
                                    </div>
                                </div>
                            </div>

                            {/* Contact Form */}
                            <div>
                                {enquirySuccess && (
                                    <div style={{
                                        backgroundColor: 'var(--success-dim)',
                                        border: '1px solid var(--success-border)',
                                        color: 'var(--success)',
                                        borderRadius: 'var(--radius-md)',
                                        padding: '1.25rem',
                                        marginBottom: '1.5rem',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.75rem'
                                    }}>
                                        <CheckCircle2 size={24} />
                                        <div>
                                            <div style={{ fontWeight: 700 }}>Thank you for your enquiry!</div>
                                            <div style={{ fontSize: '0.85rem' }}>Your message has been safely logged in our enquiry database.</div>
                                        </div>
                                    </div>
                                )}

                                {enquiryError && (
                                    <div className="alert alert-danger" style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <AlertTriangle size={18} />
                                        <span>{enquiryError}</span>
                                    </div>
                                )}

                                <form onSubmit={handleContactSubmit}>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                        <div>
                                            <label className="form-label" style={{ fontSize: '0.85rem' }}>Your Name *</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. Jane Doe"
                                                required
                                                value={contactForm.name}
                                                onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                                            />
                                        </div>
                                        <div>
                                            <label className="form-label" style={{ fontSize: '0.85rem' }}>Email Address *</label>
                                            <input
                                                type="email"
                                                className="form-control"
                                                placeholder="e.g. jane@domain.com"
                                                required
                                                value={contactForm.email}
                                                onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                                            />
                                        </div>
                                    </div>

                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                                        <div>
                                            <label className="form-label" style={{ fontSize: '0.85rem' }}>Phone Number</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. +977 9800000000"
                                                value={contactForm.phone}
                                                onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                                            />
                                        </div>
                                        <div>
                                            <label className="form-label" style={{ fontSize: '0.85rem' }}>Subject *</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                placeholder="e.g. Disputed Verdict / General Feedback"
                                                required
                                                value={contactForm.subject}
                                                onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                                            />
                                        </div>
                                    </div>

                                    <div style={{ marginBottom: '1.5rem' }}>
                                        <label className="form-label" style={{ fontSize: '0.85rem' }}>Your Message *</label>
                                        <textarea
                                            className="form-textarea"
                                            rows={4}
                                            placeholder="Provide details about your query, article feedback, or collaboration interest..."
                                            required
                                            value={contactForm.message}
                                            onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                                        />
                                    </div>

                                    <Button
                                        type="submit"
                                        variant="primary"
                                        style={{ width: '100%' }}
                                        disabled={isSubmittingEnquiry}
                                        icon={Send}
                                    >
                                        {isSubmittingEnquiry ? 'Submitting Enquiry...' : 'Submit Contact Enquiry'}
                                    </Button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Public Footer */}
            <footer style={{
                backgroundColor: 'var(--bg-header)',
                borderTop: '1px solid var(--border-subtle)',
                padding: '2rem',
                textAlign: 'center',
                color: 'var(--text-dim)',
                fontSize: '0.875rem'
            }}>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '0.75rem' }}>
                    <button onClick={scrollToHome} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                        Home
                    </button>
                    <button onClick={scrollToAbout} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                        About &amp; Methodology
                    </button>
                    <button onClick={scrollToAbout} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                        Contact Us
                    </button>
                </div>
                <div>&copy; {new Date().getFullYear()} TruthLens &bull; Automated Fake News Detection &amp; Editorial Intelligence Platform. All rights reserved.</div>
            </footer>
        </div>
    );
};
