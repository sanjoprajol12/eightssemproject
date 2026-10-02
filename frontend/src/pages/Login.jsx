import React, { useState } from 'react';
import { Shield, ArrowRight, AlertCircle, Sparkles, Eye, EyeOff, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { ThemeSwitcher } from '../components/common/ThemeSwitcher';
import { Button } from '../components/common/Button';

export const Login = ({ onNavigateToRegister, onNavigateToDetector }) => {
    const { login } = useAuth();
    const [email, setEmail] = useState('pashupati@python.py');
    const [password, setPassword] = useState('Forgot911!');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login({ email, password });
        } catch (err) {
            setError(err.message || 'Invalid administrator credentials.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-page-container">
            <nav className="auth-nav">
                <a 
                    href="#detector" 
                    className="auth-nav-brand"
                    onClick={(e) => {
                        e.preventDefault();
                        if (onNavigateToDetector) onNavigateToDetector();
                    }}
                >
                    <span className="brand-logo-icon">🔍</span>
                    <span>TruthLens</span>
                </a>
                <div className="auth-nav-right">
                    <ThemeSwitcher />
                    {onNavigateToDetector && (
                        <button 
                            type="button" 
                            className="btn btn-secondary btn-sm"
                            onClick={onNavigateToDetector}
                        >
                            <Search size={14} />
                            <span>Public Detector</span>
                        </button>
                    )}
                </div>
            </nav>

            <main className="auth-main">
                <div className="auth-box">
                    <div className="auth-header">
                        <div className="auth-brand-mark">
                            <Shield size={26} />
                        </div>
                        <h1 className="auth-title">TruthLens Admin</h1>
                        <p className="auth-subtitle">Enterprise Fake News Detection & CMS Administration</p>
                    </div>

                    <div className="glass-card">
                        {error && (
                            <div className="badge badge-danger" style={{ width: '100%', padding: '0.75rem 1rem', marginBottom: '1.25rem', borderRadius: 'var(--radius-sm)' }}>
                                <AlertCircle size={16} />
                                <span>{error}</span>
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label" htmlFor="login-email">Admin Email or Username</label>
                                <input
                                    id="login-email"
                                    type="text"
                                    className="form-control"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="pashupati@python.py"
                                    required
                                />
                            </div>

                            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                                <label className="form-label" htmlFor="login-password">Password</label>
                                <div className="password-wrap">
                                    <input
                                        id="login-password"
                                        type={showPassword ? 'text' : 'password'}
                                        className="form-control"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••"
                                        required
                                    />
                                    <button
                                        type="button"
                                        className="password-toggle-btn"
                                        onClick={() => setShowPassword(!showPassword)}
                                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                                        title={showPassword ? 'Hide password' : 'Show password'}
                                    >
                                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                isLoading={isLoading}
                                icon={ArrowRight}
                                style={{ width: '100%', padding: '0.85rem' }}
                            >
                                Sign In to Admin
                            </Button>
                        </form>

                        <div className="auth-divider">
                            <span>Don't have an account?</span>
                        </div>

                        <div className="auth-footer-links">
                            <button type="button" onClick={onNavigateToRegister}>
                                Register as Administrator
                            </button>
                        </div>

                        <div className="auth-credentials-hint">
                            <div className="auth-credentials-hint-header">
                                <Sparkles size={14} style={{ color: 'var(--primary)' }} />
                                <span>Pre-Seeded Senior Admin Credentials:</span>
                            </div>
                            <div>Email: <strong style={{ color: 'var(--text-primary)' }}>pashupati@python.py</strong></div>
                            <div>Password: <strong style={{ color: 'var(--text-primary)' }}>Forgot911!</strong></div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

