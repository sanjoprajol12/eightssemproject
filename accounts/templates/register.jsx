import React, { useState } from 'react';
import { UserPlus, User, Mail, Lock, Phone, MapPin, FileText, ArrowRight, AlertCircle, Eye, EyeOff, ArrowLeft } from 'lucide-react';

export const Register = ({ onNavigateToLogin, onNavigateToDetector }) => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        phone: '',
        address: '',
        note: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setIsLoading(true);

        try {
            const res = await fetch('/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await res.json();

            if (res.ok) {
                setSuccess('Account created successfully! Redirecting to login...');
                setTimeout(() => {
                    if (onNavigateToLogin) {
                        onNavigateToLogin();
                    } else {
                        window.location.href = '/login/';
                    }
                }, 1000);
            } else {
                setError(data.message || 'Registration failed.');
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
                    <a 
                        href="/login/" 
                        className="btn btn-secondary btn-sm nav-back"
                        onClick={(e) => {
                            if (onNavigateToLogin) {
                                e.preventDefault();
                                onNavigateToLogin();
                            }
                        }}
                    >
                        ← Back to Login
                    </a>
                </div>
            </nav>

            <main className="auth-main">
                <div className="auth-box register-wrap">
                    <div className="auth-header register-header">
                        <div className="auth-brand-mark brand-mark">
                            <UserPlus size={26} />
                        </div>
                        <h1 className="auth-title">Create Account</h1>
                        <p className="auth-subtitle">Register as an admin to manage articles and access analytics</p>
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
                            <div className="form-row auth-form-row">
                                <div className="form-group">
                                    <label className="form-label" htmlFor="reg-name">Full name *</label>
                                    <input
                                        id="reg-name"
                                        name="name"
                                        type="text"
                                        className="form-control"
                                        placeholder="Jane Smith"
                                        value={formData.name}
                                        onChange={handleChange}
                                        required
                                        autoComplete="name"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label" htmlFor="reg-phone">Phone</label>
                                    <input
                                        id="reg-phone"
                                        name="phone"
                                        type="text"
                                        className="form-control"
                                        placeholder="+1 555 0100"
                                        value={formData.phone}
                                        onChange={handleChange}
                                        autoComplete="tel"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label" htmlFor="reg-email">Email address *</label>
                                <input
                                    id="reg-email"
                                    name="email"
                                    type="email"
                                    className="form-control"
                                    placeholder="jane@example.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    autoComplete="email"
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label" htmlFor="reg-password">Password *</label>
                                <div className="password-wrap">
                                    <input
                                        id="reg-password"
                                        name="password"
                                        type={showPassword ? 'text' : 'password'}
                                        className="form-control"
                                        placeholder="Choose a strong password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        required
                                        autoComplete="new-password"
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

                            <div className="form-group">
                                <label className="form-label" htmlFor="reg-address">Address</label>
                                <input
                                    id="reg-address"
                                    name="address"
                                    type="text"
                                    className="form-control"
                                    placeholder="123 Main St, City"
                                    value={formData.address}
                                    onChange={handleChange}
                                    autoComplete="street-address"
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label" htmlFor="reg-note">Note (optional)</label>
                                <textarea
                                    id="reg-note"
                                    name="note"
                                    className="form-control form-textarea"
                                    placeholder="Any additional information..."
                                    value={formData.note}
                                    onChange={handleChange}
                                />
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
                                        <span>Create Account</span>
                                        <ArrowRight size={16} />
                                    </span>
                                )}
                            </button>
                        </form>

                        <div className="auth-divider divider">
                            <span>Already have an account?</span>
                        </div>

                        <div className="auth-footer-links login-link">
                            <a 
                                href="/login/"
                                onClick={(e) => {
                                    if (onNavigateToLogin) {
                                        e.preventDefault();
                                        onNavigateToLogin();
                                    }
                                }}
                            >
                                Sign in instead
                            </a>
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

export default Register;
