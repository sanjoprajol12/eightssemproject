import React, { useState } from 'react';
import { UserPlus, User, Mail, Lock, Phone, MapPin, FileText, ArrowRight, AlertCircle, CheckCircle2, Eye, EyeOff } from 'lucide-react';
import { api } from '../services/api';
import { ThemeSwitcher } from '../components/common/ThemeSwitcher';
import { Button } from '../components/common/Button';
import { useToast } from '../components/common/Toast';

export const RegisterPage = ({ onNavigateToLogin, onNavigateToDetector }) => {
    const { addToast } = useToast();
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
            const res = await api.register(formData);
            setSuccess('Account created successfully! Redirecting to login...');
            addToast('Registration successful! You can now log in.', 'success');
            setTimeout(() => {
                if (onNavigateToLogin) {
                    onNavigateToLogin();
                }
            }, 1200);
        } catch (err) {
            const msg = err.data?.message || err.message || 'Registration failed. Please check your details.';
            setError(msg);
            addToast(msg, 'error');
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
                    <button 
                        type="button" 
                        className="btn btn-secondary btn-sm"
                        onClick={onNavigateToLogin}
                    >
                        ← Back to Login
                    </button>
                </div>
            </nav>

            <main className="auth-main">
                <div className="auth-box">
                    <div className="auth-header">
                        <div className="auth-brand-mark">
                            <UserPlus size={26} />
                        </div>
                        <h1 className="auth-title">Create Account</h1>
                        <p className="auth-subtitle">Register as an administrator to manage articles, modules, and access analytics</p>
                    </div>

                    <div className="glass-card">
                        {error && (
                            <div className="badge badge-danger" style={{ width: '100%', padding: '0.75rem 1rem', marginBottom: '1.25rem', borderRadius: 'var(--radius-sm)' }}>
                                <AlertCircle size={16} />
                                <span>{error}</span>
                            </div>
                        )}

                        {success && (
                            <div className="badge badge-success" style={{ width: '100%', padding: '0.75rem 1rem', marginBottom: '1.25rem', borderRadius: 'var(--radius-sm)' }}>
                                <CheckCircle2 size={16} />
                                <span>{success}</span>
                            </div>
                        )}

                        <form onSubmit={handleSubmit}>
                            <div className="auth-form-row">
                                <div className="form-group">
                                    <label className="form-label" htmlFor="reg-name">Full Name *</label>
                                    <div className="input-with-icon">
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
                                </div>

                                <div className="form-group">
                                    <label className="form-label" htmlFor="reg-phone">Phone</label>
                                    <div className="input-with-icon">
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
                            </div>

                            <div className="form-group">
                                <label className="form-label" htmlFor="reg-email">Email Address *</label>
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
                                    placeholder="Any additional administrator or profile notes..."
                                    value={formData.note}
                                    onChange={handleChange}
                                />
                            </div>

                            <Button
                                type="submit"
                                variant="primary"
                                isLoading={isLoading}
                                icon={ArrowRight}
                                className="w-100"
                                style={{ width: '100%', marginTop: '0.75rem', padding: '0.85rem' }}
                            >
                                Create Account
                            </Button>
                        </form>

                        <div className="auth-divider">
                            <span>Already have an account?</span>
                        </div>

                        <div className="auth-footer-links">
                            <button type="button" onClick={onNavigateToLogin}>
                                Sign in instead
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};
