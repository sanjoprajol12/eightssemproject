import React, { useState } from 'react';
import { Shield, Lock, Mail, ArrowRight, AlertCircle, Sparkles, Eye, EyeOff, Search } from 'lucide-react';

export const Login = ({ onNavigateToRegister, onNavigateToDetector, onLoginSuccess }) => {
    const [email, setEmail] = useState('pashupati@python.py');
    const [password, setPassword] = useState('Forgot911!');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setIsLoading(true);

        try {
            const res = await fetch('/login-view/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();

            if (res.ok && data.message === 'Login successful') {
                setSuccess('Signed in successfully! Redirecting...');
                if (onLoginSuccess) {
                    onLoginSuccess(data);
                } else {
                    setTimeout(() => {
                        window.location.href = '/dashboard/';
                    }, 800);
                }
            } else {
                setError(data.message || 'Invalid email or password.');
            }
        } catch (err) {
            setError('Network error. Check that the server is running.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="auth-page-container">
            <nav className="auth-nav">
                <a 
                    href="/" 
                    className="auth-nav-brand"
                    onClick={(e) => {
                        if (onNavigateToDetector) {
                            e.preventDefault();
                            onNavigateToDetector();
                        }
                    }}
                >
                    <span className="brand-logo-icon">🔍</span>
                    <span>TruthLens</span>
                </a>
                <div className="auth-nav-right">
                    <button 
                        type="button" 
                        className="btn btn-secondary btn-sm"
                        onClick={() => {
                            if (onNavigateToDetector) onNavigateToDetector();
                            else window.location.href = '/';
                        }}
                    >
                        <Search size={14} />
                        <span>Public Detector</span>
                    </button>
                </div>
            </nav>

            <main className="auth-main">
                <div className="auth-box">
                    <div className="auth-header">
                        <div className="auth-brand-mark">
                            <Shield size={26} />
                        </div>
                        <h1 className="auth-title">Admin Login</h1>
                        <p className="auth-subtitle">Sign in to manage articles and view analytics</p>
                    </div>

                    <div className="glass-card card">
                        {error && (
                            <div className="alert alert-error" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                                <AlertCircle size={16} />
                                <span>{error}</span>
                            </div>
                        )}

                        {success && (
                            <div className="alert alert-success" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                                <span>{success}</span>
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label" htmlFor="login-email">Email address</label>
                                <input
                                    id="login-email"
                                    type="text"
                                    className="form-control"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="pashupati@python.py"
                                    required
                                    autoComplete="email"
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
                                        placeholder="Enter your password"
                                        required
                                        autoComplete="current-password"
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

                            <button
                                type="submit"
                                className="btn-submit"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <div className="spinner" style={{ display: 'block' }}></div>
                                ) : (
                                    <span className="btn-label" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span>Sign In</span>
                                        <ArrowRight size={16} />
                                    </span>
                                )}
                            </button>
                        </form>

                        <div className="auth-divider divider">
                            <span>New to TruthLens?</span>
                        </div>

                        <div className="auth-footer-links register-link">
                            <a 
                                href="/register/" 
                                onClick={(e) => {
                                    if (onNavigateToRegister) {
                                        e.preventDefault();
                                        onNavigateToRegister();
                                    }
                                }}
                            >
                                Create an admin account
                            </a>
                        </div>

                        <div className="auth-credentials-hint" style={{ marginTop: '1.5rem' }}>
                            <div className="auth-credentials-hint-header" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}>
                                <Sparkles size={14} style={{ color: 'var(--accent, #6366f1)' }} />
                                <span>Pre-Seeded Senior Admin Credentials:</span>
                            </div>
                            <div>Email: <strong style={{ color: 'var(--text-strong, #ffffff)' }}>pashupati@python.py</strong></div>
                            <div>Password: <strong style={{ color: 'var(--text-strong, #ffffff)' }}>Forgot911!</strong></div>
                        </div>
                    </div>
                </div>
            </main>

            <footer>
                TruthLens &bull; <a href="/">Detector</a>
            </footer>
        </div>
    );
};

export default Login;
