import React, { useState, useEffect, useRef } from 'react';
import {
    Play, Square, RefreshCw, Terminal, CheckCircle2,
    AlertCircle, Clock, Cpu, BarChart3, Copy, Check, X
} from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

export const TrainingModal = ({ isOpen, onClose, onTrainingCompleted }) => {
    const [status, setStatus] = useState('idle'); // 'idle' | 'running' | 'completed' | 'failed'
    const [isRunning, setIsRunning] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0.0);
    const [progress, setProgress] = useState(0);
    const [currentStep, setCurrentStep] = useState('Ready to train');
    const [logs, setLogs] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [isCopied, setIsCopied] = useState(false);

    const logEndRef = useRef(null);
    const pollIntervalRef = useRef(null);
    const timerIntervalRef = useRef(null);
    const startTimeRef = useRef(null);

    // Auto-scroll logs
    useEffect(() => {
        if (logEndRef.current) {
            logEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    // Check status on modal open
    useEffect(() => {
        if (isOpen) {
            fetchStatus();
        } else {
            clearInterval(pollIntervalRef.current);
            clearInterval(timerIntervalRef.current);
        }
        return () => {
            clearInterval(pollIntervalRef.current);
            clearInterval(timerIntervalRef.current);
        };
    }, [isOpen]);

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/models/train/status/?since=0');
            if (res.ok) {
                const data = await res.json();
                setStatus(data.status);
                setIsRunning(data.is_running);
                setProgress(data.progress);
                setCurrentStep(data.current_step);
                setLogs(data.logs || []);
                setMetrics(data.metrics);
                setElapsedTime(data.elapsed_seconds || 0.0);

                if (data.is_running) {
                    startPolling();
                }
            }
        } catch (err) {
            console.error('Failed to fetch training status:', err);
        }
    };

    const startPolling = () => {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = setInterval(async () => {
            try {
                const res = await fetch('/api/models/train/status/?since=0');
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data.status);
                    setIsRunning(data.is_running);
                    setProgress(data.progress);
                    setCurrentStep(data.current_step);
                    setLogs(data.logs || []);
                    setMetrics(data.metrics);
                    setElapsedTime(data.elapsed_seconds || 0.0);

                    if (!data.is_running) {
                        clearInterval(pollIntervalRef.current);
                        if (data.status === 'completed' && onTrainingCompleted) {
                            onTrainingCompleted(data);
                        }
                    }
                }
            } catch (err) {
                console.error('Polling error:', err);
            }
        }, 800);
    };

    const handleStartTraining = async () => {
        setIsRunning(true);
        setStatus('running');
        setProgress(5);
        setCurrentStep('Launching worker process...');
        setLogs([]);
        setElapsedTime(0.0);
        startTimeRef.current = Date.now();

        // Local live stopwatch
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = setInterval(() => {
            if (startTimeRef.current) {
                const sec = (Date.now() - startTimeRef.current) / 1000;
                setElapsedTime(parseFloat(sec.toFixed(1)));
            }
        }, 100);

        try {
            const res = await fetch('/api/models/train/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (res.ok) {
                startPolling();
            } else {
                const data = await res.json().catch(() => ({}));
                setStatus('failed');
                setIsRunning(false);
                clearInterval(timerIntervalRef.current);
                setCurrentStep(data.message || 'Failed to start training');
            }
        } catch (err) {
            console.error('Start training error:', err);
            setStatus('failed');
            setIsRunning(false);
            clearInterval(timerIntervalRef.current);
            setCurrentStep(err.message || 'Network error');
        }
    };

    const handleCopyLogs = () => {
        const text = logs.map(l => `[${l.time}] ${l.text}`).join('\n');
        navigator.clipboard.writeText(text);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = (seconds % 60).toFixed(1);
        const paddedSecs = secs < 10 ? `0${secs}` : secs;
        return `${mins < 10 ? '0' : ''}${mins}:${paddedSecs}s`;
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="TruthLens Machine Learning Model Trainer"
            size="lg"
        >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* Header Metrics / Status Bar */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                    gap: '0.85rem'
                }}>
                    {/* Status Card */}
                    <div style={{
                        padding: '0.85rem 1rem',
                        background: 'var(--bg-surface-elevated, rgba(255,255,255,0.03))',
                        border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                        borderRadius: '0.65rem'
                    }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Engine State
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.35rem' }}>
                            {isRunning ? (
                                <Badge variant="warning">
                                    <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b', animation: 'pulse 1s infinite' }} />
                                    Training Running
                                </Badge>
                            ) : status === 'completed' ? (
                                <Badge variant="success">
                                    <CheckCircle2 size={13} style={{ marginRight: '4px' }} />
                                    Model Trained
                                </Badge>
                            ) : status === 'failed' ? (
                                <Badge variant="danger">
                                    <AlertCircle size={13} style={{ marginRight: '4px' }} />
                                    Training Error
                                </Badge>
                            ) : (
                                <Badge variant="neutral">Ready to Launch</Badge>
                            )}
                        </div>
                    </div>

                    {/* Elapsed Time Stopwatch */}
                    <div style={{
                        padding: '0.85rem 1rem',
                        background: 'var(--bg-surface-elevated, rgba(255,255,255,0.03))',
                        border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                        borderRadius: '0.65rem'
                    }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Execution Time
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.35rem', fontFamily: 'monospace', fontSize: '1.15rem', fontWeight: '700', color: isRunning ? '#38bdf8' : 'var(--text-primary)' }}>
                            <Clock size={16} />
                            {formatTime(elapsedTime)}
                        </div>
                    </div>

                    {/* Accuracy (if available) */}
                    <div style={{
                        padding: '0.85rem 1rem',
                        background: 'var(--bg-surface-elevated, rgba(255,255,255,0.03))',
                        border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                        borderRadius: '0.65rem'
                    }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Model Accuracy
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.35rem', fontWeight: '700', fontSize: '1.15rem', color: metrics?.accuracy ? '#10b981' : 'var(--text-secondary)' }}>
                            <BarChart3 size={16} />
                            {metrics?.accuracy ? `${metrics.accuracy.toFixed(2)}%` : 'Pending'}
                        </div>
                    </div>

                    {/* Dataset Volume */}
                    <div style={{
                        padding: '0.85rem 1rem',
                        background: 'var(--bg-surface-elevated, rgba(255,255,255,0.03))',
                        border: '1px solid var(--border-color, rgba(255,255,255,0.08))',
                        borderRadius: '0.65rem'
                    }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Corpus Samples
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.35rem', fontWeight: '700', fontSize: '1.15rem', color: 'var(--text-primary)' }}>
                            <Cpu size={16} />
                            {metrics?.train_samples ? `${metrics.train_samples.toLocaleString()} train / ${metrics.test_samples?.toLocaleString()} test` : '10,240 train'}
                        </div>
                    </div>
                </div>

                {/* Progress Bar & Status Text */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            {isRunning && <span className="spinner" style={{ width: '12px', height: '12px' }} />}
                            {currentStep}
                        </span>
                        <span style={{ fontWeight: '600', color: '#6366f1' }}>{progress}%</span>
                    </div>
                    <div style={{
                        width: '100%',
                        height: '7px',
                        backgroundColor: 'rgba(255,255,255,0.08)',
                        borderRadius: '4px',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            width: `${progress}%`,
                            height: '100%',
                            background: isRunning
                                ? 'linear-gradient(90deg, #6366f1, #06b6d4, #10b981)'
                                : status === 'completed' ? '#10b981' : '#ef4444',
                            transition: 'width 0.4s ease-in-out'
                        }} />
                    </div>
                </div>

                {/* Terminal Console View */}
                <div style={{
                    backgroundColor: '#0a0d14',
                    border: '1px solid rgba(255,255,255,0.12)',
                    borderRadius: '0.75rem',
                    overflow: 'hidden',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                }}>
                    {/* Terminal Top Bar */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '0.6rem 0.9rem',
                        backgroundColor: '#121620',
                        borderBottom: '1px solid rgba(255,255,255,0.08)'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f59e0b' }} />
                            <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#10b981' }} />
                            <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', fontFamily: 'monospace', color: '#94a3b8' }}>
                                python train_model.py — TruthLens Classifier Pipeline
                            </span>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                                onClick={handleCopyLogs}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#94a3b8',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.3rem',
                                    fontSize: '0.75rem'
                                }}
                                title="Copy all logs"
                            >
                                {isCopied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                                {isCopied ? 'Copied' : 'Copy'}
                            </button>
                        </div>
                    </div>

                    {/* Terminal Output */}
                    <div style={{
                        padding: '1rem',
                        height: '260px',
                        overflowY: 'auto',
                        fontFamily: '"JetBrains Mono", Consolas, "Courier New", monospace',
                        fontSize: '0.82rem',
                        lineHeight: '1.5',
                        color: '#e2e8f0',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word'
                    }}>
                        {logs.length === 0 ? (
                            <div style={{ color: '#64748b', fontStyle: 'italic' }}>
                                Terminal idle. Click "Launch Training Pipeline" below to start training the TF-IDF and multi-classifier ensemble on benchmark datasets.
                            </div>
                        ) : (
                            logs.map((log, idx) => {
                                let color = '#94a3b8';
                                if (log.level === 'success' || log.text.includes('Accuracy') || log.text.includes('[DONE]') || log.text.includes('complete')) {
                                    color = '#34d399';
                                } else if (log.level === 'error' || log.text.includes('Exception') || log.text.includes('Error')) {
                                    color = '#f87171';
                                } else if (log.text.startsWith('[') || log.text.startsWith('🚀') || log.text.startsWith('⚡')) {
                                    color = '#38bdf8';
                                } else if (log.text.includes('Classification Report')) {
                                    color = '#fbbf24';
                                }

                                return (
                                    <div key={idx} style={{ marginBottom: '2px', display: 'flex', gap: '0.6rem' }}>
                                        <span style={{ color: '#475569', userSelect: 'none', minWidth: '60px' }}>
                                            {log.time}
                                        </span>
                                        <span style={{ color }}>{log.text}</span>
                                    </div>
                                );
                            })
                        )}
                        <div ref={logEndRef} />
                    </div>
                </div>

                {/* Footer Controls */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        Target artifact: <code style={{ color: '#6366f1', background: 'rgba(99,102,241,0.1)', padding: '2px 6px', borderRadius: '4px' }}>final_model.sav</code>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <Button
                            variant="secondary"
                            onClick={onClose}
                        >
                            Close Window
                        </Button>
                        <Button
                            variant="primary"
                            onClick={handleStartTraining}
                            disabled={isRunning}
                            style={{
                                background: isRunning
                                    ? 'var(--text-secondary)'
                                    : 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                                boxShadow: isRunning ? 'none' : '0 4px 16px rgba(99,102,241,0.4)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            {isRunning ? (
                                <>
                                    <span className="spinner" style={{ width: '14px', height: '14px' }} />
                                    Training in Progress...
                                </>
                            ) : (
                                <>
                                    <Play size={16} fill="currentColor" />
                                    {status === 'completed' ? 'Re-run Model Training' : 'Launch Training Pipeline'}
                                </>
                            )}
                        </Button>
                    </div>
                </div>
            </div>
        </Modal>
    );
};
