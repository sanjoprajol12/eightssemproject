import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    Cpu, Database, Play, RefreshCw, CheckCircle2, AlertTriangle,
    Search, ChevronLeft, ChevronRight
} from 'lucide-react';
import { StatCard } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { TrainingModal } from '../components/training/TrainingModal';
import { useToast } from '../components/common/Toast';

export const TotalModelsPage = () => {
    const { showToast } = useToast();

    // Summary & Models state
    const [summary, setSummary] = useState(null);
    const [models, setModels] = useState([]);
    const [isSummaryLoading, setIsSummaryLoading] = useState(false);

    // Paginated Dataset table state
    const [datasetRows, setDatasetRows] = useState([]);
    const [_sourcesList, setSourcesList] = useState([]);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(15);
    const [totalPages, setTotalPages] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const [counts, setCounts] = useState({ total: 0, real: 0, fake: 0 });
    const [isDataLoading, setIsDataLoading] = useState(false);

    const [searchTerm, setSearchTerm] = useState('');
    const searchTermRef = useRef(searchTerm);
    useEffect(() => {
        searchTermRef.current = searchTerm;
    }, [searchTerm]);

    const [labelFilter, setLabelFilter] = useState('all'); // 'all' | 'real' | 'fake'
    const [sourceFilter, setSourceFilter] = useState('all');

    // Training Modal state
    const [isTrainModalOpen, setIsTrainModalOpen] = useState(false);

    // Fetch models summary from backend
    const fetchSummary = useCallback(async () => {
        setIsSummaryLoading(true);
        try {
            const res = await fetch('/api/models/summary/');
            if (res.ok) {
                const data = await res.json();
                setSummary(data.summary);
                setModels(data.models || []);
            }
        } catch (err) {
            console.error('Failed to load models summary:', err);
            showToast('Unable to load models summary', 'error');
        } finally {
            setIsSummaryLoading(false);
        }
    }, [showToast]);

    // Fetch server-side paginated & filtered dataset
    const fetchDataset = useCallback(async (targetPage = page, search = searchTerm, label = labelFilter, source = sourceFilter, size = pageSize) => {
        setIsDataLoading(true);
        try {
            const params = new URLSearchParams({
                page: targetPage.toString(),
                page_size: size.toString(),
                search: search.trim(),
                label: label,
                source: source
            });

            const res = await fetch(`/api/models/data/?${params.toString()}`);
            if (res.ok) {
                const data = await res.json();
                setDatasetRows(data.results || []);
                setTotalCount(data.total || 0);
                setTotalPages(data.total_pages || 1);
                setPage(data.page || 1);
                setCounts(data.counts || { total: 0, real: 0, fake: 0 });
                if (data.sources) setSourcesList(data.sources);
            }
        } catch (err) {
            console.error('Failed to load dataset:', err);
            showToast('Unable to load dataset records', 'error');
        } finally {
            setIsDataLoading(false);
        }
    }, [page, searchTerm, labelFilter, sourceFilter, pageSize, showToast]);

    useEffect(() => {
        let isMounted = true;
        fetch('/api/models/summary/')
            .then(res => res.ok ? res.json() : Promise.reject(new Error('Failed')))
            .then(data => {
                if (!isMounted) return;
                setSummary(data.summary);
                setModels(data.models || []);
            })
            .catch(err => {
                console.error('Failed to load models summary:', err);
                if (isMounted) showToast('Unable to load models summary', 'error');
            })
            .finally(() => {
                if (isMounted) setIsSummaryLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [showToast]);

    useEffect(() => {
        let isMounted = true;
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString(),
            search: searchTermRef.current.trim(),
            label: labelFilter,
            source: sourceFilter
        });

        fetch(`/api/models/data/?${params.toString()}`)
            .then(res => res.ok ? res.json() : Promise.reject(new Error('Failed')))
            .then(data => {
                if (!isMounted) return;
                setDatasetRows(data.results || []);
                setTotalCount(data.total || 0);
                setTotalPages(data.total_pages || 1);
                setPage(data.page || 1);
                setCounts(data.counts || { total: 0, real: 0, fake: 0 });
                if (data.sources) setSourcesList(data.sources);
            })
            .catch(err => {
                console.error('Failed to load dataset:', err);
                if (isMounted) showToast('Unable to load dataset records', 'error');
            })
            .finally(() => {
                if (isMounted) setIsDataLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [page, labelFilter, sourceFilter, pageSize, showToast]);

    // Handle search input with manual trigger or Enter
    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        setPage(1);
        fetchDataset(1, searchTerm, labelFilter, sourceFilter, pageSize);
    };

    const handleTrainingCompleted = () => {
        showToast('Model training completed! Refreshing metrics...', 'success');
        fetchSummary();
        fetchDataset(page, searchTerm, labelFilter, sourceFilter, pageSize);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Top Page Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                flexWrap: 'wrap',
                gap: '1rem',
                borderBottom: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                paddingBottom: '1.25rem'
            }}>
                <div>
                    <h1 style={{
                        fontSize: '1.85rem',
                        fontWeight: '800',
                        color: 'var(--text-primary)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.65rem'
                    }}>
                        <Cpu className="text-primary" size={28} />
                        Total Models & Dataset Analytics
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.35rem', fontSize: '0.92rem' }}>
                        Multi-classifier model inventory, real vs fake counts, and server-side paginated benchmark data.
                    </p>
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <Button
                        variant="secondary"
                        onClick={() => {
                            fetchSummary();
                            fetchDataset(page, searchTerm, labelFilter, sourceFilter, pageSize);
                            showToast('Refreshed model metrics', 'info');
                        }}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                        <RefreshCw size={15} className={isSummaryLoading ? 'spinner' : ''} />
                        Refresh
                    </Button>

                    <Button
                        variant="primary"
                        onClick={() => setIsTrainModalOpen(true)}
                        style={{
                            background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                            boxShadow: '0 4px 16px rgba(99,102,241,0.4)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            fontWeight: '600'
                        }}
                    >
                        <Play size={16} fill="currentColor" />
                        Launch Training Pipeline
                    </Button>
                </div>
            </div>

            {/* Quick Stat Highlights */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '1.25rem'
            }}>
                <StatCard
                    icon={Cpu}
                    title="Active ML Classifiers"
                    value={summary?.total_models ? `${summary.total_models} Models` : '6 Models'}
                    color="primary"
                />
                <StatCard
                    icon={Database}
                    title="Total Benchmark Statements"
                    value={summary?.total_dataset_samples ? summary.total_dataset_samples.toLocaleString() : '14,026'}
                    color="accent"
                />
                <StatCard
                    icon={CheckCircle2}
                    title="Total Real News Count"
                    value={summary?.total_real_count ? summary.total_real_count.toLocaleString() : '7,783'}
                    color="success"
                />
                <StatCard
                    icon={AlertTriangle}
                    title="Total Fake News Count"
                    value={summary?.total_fake_count ? summary.total_fake_count.toLocaleString() : '6,243'}
                    color="danger"
                />
            </div>

            {/* Model Inventory Cards Grid */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                        Configured Models Breakdown & Real/Fake Counts
                    </h2>
                    <Badge variant="neutral">6 Active Engines</Badge>
                </div>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                    gap: '1.25rem'
                }}>
                    {models.map((model) => {
                        const realRatio = model.total_samples > 0
                            ? Math.round((model.real_count / model.total_samples) * 100)
                            : 50;
                        const fakeRatio = 100 - realRatio;

                        return (
                            <div
                                key={model.id}
                                style={{
                                    backgroundColor: 'var(--bg-surface, #1e2433)',
                                    border: model.is_primary ? '1px solid rgba(99,102,241,0.4)' : '1px solid var(--border-color, rgba(255,255,255,0.08))',
                                    borderRadius: '0.85rem',
                                    padding: '1.25rem',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '1rem',
                                    position: 'relative',
                                    boxShadow: model.is_primary ? '0 4px 20px rgba(99,102,241,0.15)' : 'none'
                                }}
                            >
                                {/* Header with Badge */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <div style={{ fontWeight: '700', fontSize: '1.05rem', color: 'var(--text-primary)' }}>
                                            {model.name}
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                            {model.type}
                                        </div>
                                    </div>
                                    <Badge variant={model.is_primary ? 'primary' : 'neutral'}>
                                        {model.status}
                                    </Badge>
                                </div>

                                {/* Accuracy & F1 metric tags */}
                                <div style={{
                                    display: 'flex',
                                    gap: '0.85rem',
                                    background: 'rgba(0,0,0,0.2)',
                                    padding: '0.65rem 0.85rem',
                                    borderRadius: '0.5rem',
                                    alignItems: 'center'
                                }}>
                                    <div style={{ flex: 1 }}>
                                        <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                                            Accuracy
                                        </span>
                                        <div style={{ fontWeight: '700', fontSize: '1.1rem', color: '#10b981' }}>
                                            {model.accuracy.toFixed(1)}%
                                        </div>
                                    </div>
                                    <div style={{ width: '1px', height: '24px', background: 'rgba(255,255,255,0.1)' }} />
                                    <div style={{ flex: 1 }}>
                                        <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                                            F1 Score
                                        </span>
                                        <div style={{ fontWeight: '700', fontSize: '1.1rem', color: '#6366f1' }}>
                                            {model.f1_score.toFixed(1)}%
                                        </div>
                                    </div>
                                    <div style={{ width: '1px', height: '24px', background: 'rgba(255,255,255,0.1)' }} />
                                    <div style={{ flex: 1.2 }}>
                                        <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                                            Total Samples
                                        </span>
                                        <div style={{ fontWeight: '700', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
                                            {model.total_samples.toLocaleString()}
                                        </div>
                                    </div>
                                </div>

                                {/* Real vs Fake Count Breakdown */}
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.4rem' }}>
                                        <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                            <CheckCircle2 size={13} />
                                            Real: <strong>{model.real_count.toLocaleString()}</strong> ({realRatio}%)
                                        </span>
                                        <span style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                            <AlertTriangle size={13} />
                                            Fake: <strong>{model.fake_count.toLocaleString()}</strong> ({fakeRatio}%)
                                        </span>
                                    </div>
                                    <div style={{
                                        width: '100%',
                                        height: '6px',
                                        backgroundColor: '#ef4444',
                                        borderRadius: '3px',
                                        overflow: 'hidden',
                                        display: 'flex'
                                    }}>
                                        <div style={{
                                            width: `${realRatio}%`,
                                            height: '100%',
                                            backgroundColor: '#10b981'
                                        }} />
                                    </div>
                                </div>

                                {/* Artifact & Features Details */}
                                <div style={{
                                    fontSize: '0.78rem',
                                    color: 'var(--text-secondary)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    borderTop: '1px solid rgba(255,255,255,0.06)',
                                    paddingTop: '0.65rem',
                                    marginTop: 'auto'
                                }}>
                                    <span>Artifact: <code style={{ color: '#38bdf8' }}>{model.artifact}</code></span>
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={() => setIsTrainModalOpen(true)}
                                        style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem', height: 'auto' }}
                                    >
                                        Train Model
                                    </Button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Server-Side Paginated Dataset Statements Section */}
            <div style={{
                backgroundColor: 'var(--bg-surface, #1e2433)',
                border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                borderRadius: '0.85rem',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '1rem'
                }}>
                    <div>
                        <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                            Server-Side Paginated Training & Benchmark Dataset
                        </h2>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                            Filtered statements from SQLite FTS5 index. Results are paginated from the backend with dynamic counts.
                        </p>
                    </div>

                    {/* Filter Summary Badges */}
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <Badge variant="neutral">
                            Total Filtered: <strong>{counts.total.toLocaleString()}</strong>
                        </Badge>
                        <Badge variant="success">
                            Real: <strong>{counts.real.toLocaleString()}</strong>
                        </Badge>
                        <Badge variant="danger">
                            Fake: <strong>{counts.fake.toLocaleString()}</strong>
                        </Badge>
                    </div>
                </div>

                {/* Filter Controls Bar */}
                <form
                    onSubmit={handleSearchSubmit}
                    style={{
                        display: 'flex',
                        gap: '0.75rem',
                        alignItems: 'center',
                        flexWrap: 'wrap',
                        background: 'rgba(0,0,0,0.15)',
                        padding: '0.75rem 1rem',
                        borderRadius: '0.65rem',
                        border: '1px solid rgba(255,255,255,0.06)'
                    }}
                >
                    {/* Search Input */}
                    <div style={{ position: 'relative', flex: '1 1 240px' }}>
                        <Search
                            size={16}
                            style={{
                                position: 'absolute',
                                left: '0.85rem',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                color: 'var(--text-secondary)'
                            }}
                        />
                        <input
                            type="text"
                            placeholder="Search statement text or keywords..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.55rem 0.75rem 0.55rem 2.4rem',
                                borderRadius: '0.5rem',
                                border: '1px solid var(--border-color, rgba(255,255,255,0.12))',
                                background: 'var(--bg-app, #111827)',
                                color: 'var(--text-primary)',
                                fontSize: '0.88rem'
                            }}
                        />
                    </div>

                    {/* Label Filter */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Label:</span>
                        <select
                            value={labelFilter}
                            onChange={(e) => {
                                setLabelFilter(e.target.value);
                                setPage(1);
                            }}
                            style={{
                                padding: '0.55rem 0.75rem',
                                borderRadius: '0.5rem',
                                border: '1px solid var(--border-color, rgba(255,255,255,0.12))',
                                background: 'var(--bg-app, #111827)',
                                color: 'var(--text-primary)',
                                fontSize: '0.85rem'
                            }}
                        >
                            <option value="all">All Statements</option>
                            <option value="real">Real News Only</option>
                            <option value="fake">Fake News Only</option>
                        </select>
                    </div>

                    {/* Source Filter */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Source:</span>
                        <select
                            value={sourceFilter}
                            onChange={(e) => {
                                setSourceFilter(e.target.value);
                                setPage(1);
                            }}
                            style={{
                                padding: '0.55rem 0.75rem',
                                borderRadius: '0.5rem',
                                border: '1px solid var(--border-color, rgba(255,255,255,0.12))',
                                background: 'var(--bg-app, #111827)',
                                color: 'var(--text-primary)',
                                fontSize: '0.85rem',
                                maxWidth: '200px'
                            }}
                        >
                            <option value="all">All Sources</option>
                            <option value="train.csv">train.csv (Benchmark)</option>
                            <option value="test.csv">test.csv (Benchmark)</option>
                            <option value="valid.csv">valid.csv (Benchmark)</option>
                            <option value="LIAR">LIAR Dataset</option>
                        </select>
                    </div>

                    {/* Page Size */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Show:</span>
                        <select
                            value={pageSize}
                            onChange={(e) => {
                                setPageSize(parseInt(e.target.value, 10));
                                setPage(1);
                            }}
                            style={{
                                padding: '0.55rem 0.65rem',
                                borderRadius: '0.5rem',
                                border: '1px solid var(--border-color, rgba(255,255,255,0.12))',
                                background: 'var(--bg-app, #111827)',
                                color: 'var(--text-primary)',
                                fontSize: '0.85rem'
                            }}
                        >
                            <option value="10">10</option>
                            <option value="15">15</option>
                            <option value="25">25</option>
                            <option value="50">50</option>
                        </select>
                    </div>

                    <Button type="submit" variant="secondary" size="sm" style={{ padding: '0.55rem 1rem' }}>
                        Apply Filter
                    </Button>
                </form>

                {/* Data Table */}
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead>
                            <tr style={{
                                borderBottom: '1px solid var(--border-color, rgba(255,255,255,0.1))',
                                color: 'var(--text-secondary)',
                                fontSize: '0.78rem',
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em'
                            }}>
                                <th style={{ padding: '0.75rem 0.5rem' }}>ID</th>
                                <th style={{ padding: '0.75rem 1rem', width: '50%' }}>Statement Text / Headline</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Classification</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Dataset Source</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Ground Truth</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Hash</th>
                            </tr>
                        </thead>
                        <tbody>
                            {isDataLoading ? (
                                <tr>
                                    <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                                        <div className="spinner" style={{ margin: '0 auto 0.75rem' }} />
                                        Loading paginated dataset records...
                                    </td>
                                </tr>
                            ) : datasetRows.length === 0 ? (
                                <tr>
                                    <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                                        No statements found matching your filter criteria.
                                    </td>
                                </tr>
                            ) : (
                                datasetRows.map((row) => (
                                    <tr
                                        key={row.id}
                                        style={{
                                            borderBottom: '1px solid rgba(255,255,255,0.04)',
                                            fontSize: '0.88rem'
                                        }}
                                    >
                                        <td style={{ padding: '0.85rem 0.5rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                                            #{row.id}
                                        </td>
                                        <td style={{ padding: '0.85rem 1rem', color: 'var(--text-primary)', fontWeight: '500' }}>
                                            <div>{row.title}</div>
                                            {row.summary && (
                                                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                                                    {row.summary}
                                                </div>
                                            )}
                                        </td>
                                        <td style={{ padding: '0.85rem 1rem' }}>
                                            {row.label === 'real' ? (
                                                <Badge variant="success">Real News</Badge>
                                            ) : (
                                                <Badge variant="danger">Fake News</Badge>
                                            )}
                                        </td>
                                        <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
                                            {row.source}
                                        </td>
                                        <td style={{ padding: '0.85rem 1rem' }}>
                                            {row.is_verified ? (
                                                <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem' }}>
                                                    <CheckCircle2 size={14} />
                                                    Verified
                                                </span>
                                            ) : (
                                                <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Standard</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                            {row.content_hash || '—'}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Server-Side Pagination Bar */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '1rem',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid rgba(255,255,255,0.06)',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)'
                }}>
                    <div>
                        Showing <strong>{datasetRows.length > 0 ? (page - 1) * pageSize + 1 : 0}</strong> to{' '}
                        <strong>{Math.min(page * pageSize, totalCount)}</strong> of{' '}
                        <strong>{totalCount.toLocaleString()}</strong> statements
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Button
                            variant="secondary"
                            size="sm"
                            disabled={page <= 1 || isDataLoading}
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', padding: '0.4rem 0.75rem' }}
                        >
                            <ChevronLeft size={16} />
                            Previous
                        </Button>

                        <span style={{ padding: '0 0.5rem', fontWeight: '600', color: 'var(--text-primary)' }}>
                            Page {page} of {totalPages}
                        </span>

                        <Button
                            variant="secondary"
                            size="sm"
                            disabled={page >= totalPages || isDataLoading}
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.2rem', padding: '0.4rem 0.75rem' }}
                        >
                            Next
                            <ChevronRight size={16} />
                        </Button>
                    </div>
                </div>
            </div>

            {/* Live Model Training Terminal Modal */}
            <TrainingModal
                isOpen={isTrainModalOpen}
                onClose={() => setIsTrainModalOpen(false)}
                onTrainingCompleted={handleTrainingCompleted}
            />
        </div>
    );
};
