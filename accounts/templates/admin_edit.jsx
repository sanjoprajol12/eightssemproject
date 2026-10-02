import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, MapPin, Shield, Key, Save, ArrowLeft, CheckCircle2, AlertCircle, Eye, EyeOff } from 'lucide-react';

export const AdminEdit = ({ adminId, onBackToDashboard }) => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
        address: '',
        note: '',
        password: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await fetch('/api/profile/');
                if (res.ok) {
                    const data = await res.json();
                    setFormData({
                        name: data.name || '',
                        email: data.email || '',
                        phone: data.phone || '',
                        address: data.address || '',
                        note: data.note || '',
                        password: ''
                    });
                }
            } catch (err) {
                console.error('Error fetching profile:', err);
            }
        };

        fetchProfile();
    }, [adminId]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setStatusMessage(null);

        try {
            const res = await fetch('/api/profile/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const data = await res.json();
            if (res.ok) {
                setStatusMessage({ type: 'success', text: 'Admin profile updated successfully!' });
            } else {
                setStatusMessage({ type: 'error', text: data.error || 'Failed to update profile.' });
            }
        } catch (err) {
            setStatusMessage({ type: 'error', text: 'Network error occurred.' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <a 
                    href="/dashboard/" 
                    className="btn btn-secondary btn-sm"
                    onClick={(e) => {
                        if (onBackToDashboard) {
                            e.preventDefault();
                            onBackToDashboard();
                        }
                    }}
                >
                    <ArrowLeft size={14} />
                    <span>Back to Dashboard</span>
                </a>
                <span className="badge badge-primary">Active Admin</span>
            </div>

            <div className="glass-card" style={{ padding: '2rem' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                    Edit Admin: {formData.name || 'Administrator'}
                </h2>
                <p style={{ color: 'var(--muted)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
                    Update administrative details, contact info, and security credentials.
                </p>

                {statusMessage && (
                    <div 
                        className={`alert alert-${statusMessage.type === 'success' ? 'success' : 'error'}`}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}
                    >
                        {statusMessage.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
                        <span>{statusMessage.text}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                        <label className="form-label" htmlFor="name">Full Name *</label>
                        <input
                            id="name"
                            name="name"
                            type="text"
                            className="form-control"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                        <label className="form-label" htmlFor="email">Email Address</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            className="form-control"
                            value={formData.email}
                            disabled
                            style={{ opacity: 0.7 }}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                        <label className="form-label" htmlFor="phone">Phone</label>
                        <input
                            id="phone"
                            name="phone"
                            type="text"
                            className="form-control"
                            value={formData.phone}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                        <label className="form-label" htmlFor="address">Address</label>
                        <textarea
                            id="address"
                            name="address"
                            className="form-control form-textarea"
                            value={formData.address}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                        <label className="form-label" htmlFor="password">Update Password</label>
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

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={isLoading}
                        >
                            <Save size={16} />
                            <span>Save Changes</span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminEdit;
