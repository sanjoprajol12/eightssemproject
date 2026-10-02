import React, { useState, useEffect } from 'react';
import {
    FileText, CheckCircle2, AlertTriangle, Activity, RefreshCw,
    Search, Plus, Trash2, Edit2, ShieldAlert, Cpu, Eye, ExternalLink, LogOut, ArrowLeft
} from 'lucide-react';

export const Dashboard = ({ onNavigateToDetector, onLogout }) => {
    const [subTab, setSubTab] = useState('articles');
    const [articles, setArticles] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchArticles = async () => {
        setIsLoading(true);
        try {
            const res = await fetch('/api/articles/');
            if (res.ok) {
                const data = await res.json();
                setArticles(Array.isArray(data) ? data : data.results || []);
            }
        } catch (err) {
            setError('Failed to fetch articles');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchArticles();
    }, []);

    const handleDeleteArticle = async (id) => {
        if (!window.confirm('Are you sure you want to delete this article?')) return;
        try {
            const res = await fetch(`/api/articles/${id}/`, { method: 'DELETE' });
            if (res.ok) {
                setArticles(prev => prev.filter(a => a.id !== id));
            }
        } catch (err) {
            alert('Failed to delete article');
        }
    };

    return (
        <div className="detector-root">
            <header className="detector-nav">
                <a href="/" className="nav-brand">
                    <span className="logo-icon">🔍</span>
                    <span>TruthLens Dashboard</span>
                </a>
                <div className="nav-right" style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <a 
                        href="/" 
                        className="btn btn-secondary btn-sm"
                        onClick={(e) => {
                            if (onNavigateToDetector) {
                                e.preventDefault();
                                onNavigateToDetector();
                            }
                        }}
                    >
                        <Search size={14} />
                        <span>Detector</span>
                    </a>
                    <a 
                        href="/logout/" 
                        className="btn btn-secondary btn-sm"
                        onClick={(e) => {
                            if (onLogout) {
                                e.preventDefault();
                                onLogout();
                            }
                        }}
                    >
                        <LogOut size={14} />
                        <span>Logout</span>
                    </a>
                </div>
            </header>

            <main className="detector-main" style={{ padding: '2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <div>
                        <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Article Repository & Verification Records</h1>
                        <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>Manage catalogued truth benchmarks and verified ground-truth sources</p>
                    </div>
                    <button 
                        className="btn btn-primary"
                        onClick={fetchArticles}
                        disabled={isLoading}
                    >
                        <RefreshCw size={15} className={isLoading ? 'spinner' : ''} />
                        <span>Refresh</span>
                    </button>
                </div>

                <div className="glass-card" style={{ padding: '1.5rem' }}>
                    {isLoading ? (
                        <div style={{ textAlign: 'center', padding: '3rem' }}>
                            <div className="spinner" style={{ margin: '0 auto 1rem', display: 'block' }}></div>
                            <p style={{ color: 'var(--muted)' }}>Loading articles...</p>
                        </div>
                    ) : articles.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--muted)' }}>
                            <FileText size={36} style={{ margin: '0 auto 0.75rem', opacity: 0.5 }} />
                            <p>No verified articles registered yet.</p>
                        </div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                        <th style={{ padding: '0.75rem 1rem' }}>Title</th>
                                        <th style={{ padding: '0.75rem 1rem' }}>Author / Source</th>
                                        <th style={{ padding: '0.75rem 1rem' }}>Confidence Rate</th>
                                        <th style={{ padding: '0.75rem 1rem' }}>Date Created</th>
                                        <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {articles.map((art) => (
                                        <tr key={art.id} style={{ borderBottom: '1px solid var(--border)' }}>
                                            <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>{art.title}</td>
                                            <td style={{ padding: '0.85rem 1rem', color: 'var(--muted)' }}>{art.username || 'System'}</td>
                                            <td style={{ padding: '0.85rem 1rem' }}>
                                                <span style={{ 
                                                    padding: '0.2rem 0.6rem', 
                                                    borderRadius: '12px', 
                                                    background: 'rgba(16,185,129,0.15)', 
                                                    color: '#10b981', 
                                                    fontSize: '0.8rem',
                                                    fontWeight: 600
                                                }}>
                                                    ★ {art.rate || '5.0'}
                                                </span>
                                            </td>
                                            <td style={{ padding: '0.85rem 1rem', color: 'var(--muted)', fontSize: '0.825rem' }}>{art.created_at}</td>
                                            <td style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>
                                                <button 
                                                    className="btn btn-ghost-sm"
                                                    style={{ color: '#f43f5e' }}
                                                    onClick={() => handleDeleteArticle(art.id)}
                                                    title="Delete"
                                                >
                                                    <Trash2 size={15} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
