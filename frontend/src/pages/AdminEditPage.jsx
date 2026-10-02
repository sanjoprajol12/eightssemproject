import React, { useState, useEffect } from 'react';
import { 
    Save, ArrowLeft, 
    CheckCircle2, AlertCircle, Eye, EyeOff 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { useToast } from '../components/common/Toast';

export const AdminEditPage = ({ onBackToDashboard }) => {
    const { user, setUser } = useAuth();
    const { addToast } = useToast();
    const [showPassword, setShowPassword] = useState(false);
    
    const [formData, setFormData] = useState({
        first_name: '',
        middle_name: '',
        last_name: '',
        username: '',
        email: '',
        phone: '',
        mobile: '',
        address: '',
        user_type: 'admin',
        access_type: 'super',
        is_mfa_enabled: false,
        is_email_authentication_enabled: false,
        password: ''
    });

    const [isLoading, setIsLoading] = useState(false);
    const [isFetching, setIsFetching] = useState(true);
    const [statusMessage, setStatusMessage] = useState(null);

    useEffect(() => {
        const fetchUserData = async () => {
            setIsFetching(true);
            try {
                const me = await api.getMe();
                setFormData({
                    first_name: me.first_name || '',
                    middle_name: me.middle_name || '',
                    last_name: me.last_name || '',
                    username: me.username || '',
                    email: me.email || '',
                    phone: me.phone || '',
                    mobile: me.mobile || '',
                    address: me.address || '',
                    user_type: me.user_type || 'admin',
                    access_type: me.access_type || 'standard',
                    is_mfa_enabled: Boolean(me.is_mfa_enabled),
                    is_email_authentication_enabled: Boolean(me.is_email_authentication_enabled),
                    password: ''
                });
            } catch {
                if (user) {
                    setFormData(prev => ({
                        ...prev,
                        first_name: user.first_name || '',
                        last_name: user.last_name || '',
                        username: user.username || '',
                        email: user.email || '',
                    }));
                }
            } finally {
                setIsFetching(false);
            }
        };

        fetchUserData();
    }, [user]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setStatusMessage(null);

        const payload = { ...formData };
        if (!payload.password) {
            delete payload.password;
        }

        try {
            const updated = await api.updateMe(payload);
            if (setUser) {
                setUser(updated);
            }
            setStatusMessage({ type: 'success', text: 'Admin profile updated successfully!' });
            addToast('Profile changes saved.', 'success');
        } catch (err) {
            const errorText = err.data?.message || err.message || 'Failed to update admin profile.';
            setStatusMessage({ type: 'error', text: errorText });
            addToast(errorText, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    if (isFetching) {
        return (
            <div className="profile-container" style={{ textAlign: 'center', padding: '4rem 1rem' }}>
                <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                <p style={{ color: 'var(--text-secondary)' }}>Loading admin profile...</p>
            </div>
        );
    }

    const displayName = [formData.first_name, formData.middle_name, formData.last_name].filter(Boolean).join(' ') || formData.username || 'Administrator';

    return (
        <div className="profile-container">
            {/* Header with back button */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <Button
                    variant="secondary"
                    icon={ArrowLeft}
                    onClick={onBackToDashboard}
                    size="sm"
                >
                    Back to Dashboard
                </Button>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <Badge variant="primary" dot>{formData.user_type.toUpperCase()}</Badge>
                    <Badge variant="success">Active</Badge>
                </div>
            </div>

            {/* Profile Hero Card */}
            <div className="glass-card profile-header-card">
                <div className="profile-avatar-large">
                    {displayName.charAt(0).toUpperCase()}
                </div>
                <div className="profile-meta">
                    <h2>Edit Admin: {displayName}</h2>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        {formData.email} • @{formData.username}
                    </p>
                    <div className="profile-badges">
                        <Badge variant="secondary">Access: {formData.access_type}</Badge>
                        {formData.is_mfa_enabled && <Badge variant="warning">MFA Active</Badge>}
                        {formData.is_email_authentication_enabled && <Badge variant="primary">Email 2FA</Badge>}
                    </div>
                </div>
            </div>

            {statusMessage && (
                <div 
                    className={`badge badge-${statusMessage.type === 'success' ? 'success' : 'danger'}`} 
                    style={{ width: '100%', padding: '0.85rem 1.25rem', borderRadius: 'var(--radius-sm)' }}
                >
                    {statusMessage.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                    <span>{statusMessage.text}</span>
                </div>
            )}

            {/* Edit Form */}
            <form onSubmit={handleSubmit} className="glass-card" style={{ padding: '2rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-primary)' }}>
                    Personal & Contact Information
                </h3>

                <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="first_name">First Name</label>
                        <input
                            id="first_name"
                            name="first_name"
                            type="text"
                            className="form-control"
                            value={formData.first_name}
                            onChange={handleChange}
                            placeholder="John"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="middle_name">Middle Name</label>
                        <input
                            id="middle_name"
                            name="middle_name"
                            type="text"
                            className="form-control"
                            value={formData.middle_name}
                            onChange={handleChange}
                            placeholder="M."
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="last_name">Last Name</label>
                        <input
                            id="last_name"
                            name="last_name"
                            type="text"
                            className="form-control"
                            value={formData.last_name}
                            onChange={handleChange}
                            placeholder="Doe"
                        />
                    </div>
                </div>

                <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="username">Username *</label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            className="form-control"
                            value={formData.username}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="email">Email Address *</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            className="form-control"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>
                </div>

                <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="phone">Phone</label>
                        <input
                            id="phone"
                            name="phone"
                            type="text"
                            className="form-control"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="+1 234 567 8900"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="mobile">Mobile</label>
                        <input
                            id="mobile"
                            name="mobile"
                            type="text"
                            className="form-control"
                            value={formData.mobile}
                            onChange={handleChange}
                            placeholder="+1 987 654 3210"
                        />
                    </div>
                </div>

                <div className="form-group" style={{ marginBottom: '2rem' }}>
                    <label className="form-label" htmlFor="address">Address</label>
                    <textarea
                        id="address"
                        name="address"
                        className="form-control form-textarea"
                        value={formData.address}
                        onChange={handleChange}
                        placeholder="Street address, City, Country"
                    />
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '1.25rem', color: 'var(--text-primary)' }}>
                    Security & Credentials
                </h3>

                <div className="form-grid" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="password">Change Password</label>
                        <div className="password-wrap">
                            <input
                                id="password"
                                name="password"
                                type={showPassword ? 'text' : 'password'}
                                className="form-control"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Leave blank to keep current password"
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
                        <label className="form-label" htmlFor="user_type">Role</label>
                        <select
                            id="user_type"
                            name="user_type"
                            className="form-select"
                            value={formData.user_type}
                            onChange={handleChange}
                        >
                            <option value="admin">Administrator</option>
                            <option value="superadmin">Super Administrator</option>
                            <option value="analyst">Analyst</option>
                            <option value="editor">Editor</option>
                        </select>
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '2rem' }}>
                    <label className="form-checkbox-label">
                        <input
                            type="checkbox"
                            name="is_mfa_enabled"
                            checked={formData.is_mfa_enabled}
                            onChange={handleChange}
                            className="form-checkbox"
                        />
                        <span>Enable Multi-Factor Authentication (MFA)</span>
                    </label>

                    <label className="form-checkbox-label">
                        <input
                            type="checkbox"
                            name="is_email_authentication_enabled"
                            checked={formData.is_email_authentication_enabled}
                            onChange={handleChange}
                            className="form-checkbox"
                        />
                        <span>Enable Email Login Verification Code</span>
                    </label>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.5rem' }}>
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={onBackToDashboard}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        variant="primary"
                        isLoading={isLoading}
                        icon={Save}
                    >
                        Save Changes
                    </Button>
                </div>
            </form>
        </div>
    );
};
