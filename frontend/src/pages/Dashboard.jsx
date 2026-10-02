import React, { useEffect, useState } from 'react';
import {
    BookOpen, Image, Users, HeartHandshake, Briefcase, Mail,
    Download, Film, Settings, Sparkles, CheckCircle, ArrowUpRight
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { StatCard, Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export const Dashboard = ({ onNavigate }) => {
    const { user } = useAuth();
    const [stats, setStats] = useState({});
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        let isMounted = true;
        api.getCmsStats()
            .then(data => {
                if (isMounted) setStats(data || {});
            })
            .catch(err => {
                console.error('Failed to load stats:', err);
            })
            .finally(() => {
                if (isMounted) setIsLoading(false);
            });
        return () => {
            isMounted = false;
        };
    }, []);

    const statItems = [
        { title: 'Total Blogs', value: stats.blogs, icon: BookOpen, resource: 'blogs' },
        { title: 'Photo Albums', value: stats.albums, icon: Image, resource: 'albums' },
        { title: 'Team Members', value: stats.teams, icon: Users, resource: 'teams' },
        { title: 'Services Offered', value: stats.services, icon: HeartHandshake, resource: 'services' },
        { title: 'Open Careers', value: stats.careers, icon: Briefcase, resource: 'careers' },
        { title: 'Applications', value: stats.career_applications, icon: Briefcase, resource: 'career-applications' },
        { title: 'Client Enquiries', value: stats.enquiries, icon: Mail, resource: 'enquiries' },
        { title: 'Media Assets', value: stats.media, icon: Film, resource: 'media' },
        { title: 'Downloads / Files', value: stats.downloads, icon: Download, resource: 'downloads' },
    ];

    return (
        <div>
            {/* Welcome Banner */}
            <div className="glass-card" style={{
                marginBottom: '2rem',
                background: 'linear-gradient(135deg, var(--bg-card), var(--primary-dim))',
                border: '1px solid var(--border-normal)',
                padding: '2rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1.25rem' }}>
                    <div>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--primary)', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                            <Sparkles size={16} />
                            <span>Enterprise Admin Portal</span>
                        </div>
                        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                            Welcome back, {user?.full_name || user?.username || 'Administrator'}!
                        </h1>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', maxWidth: '650px' }}>
                            Fack News Detection is active with full Python backend architecture, 25 modular CMS CRUD endpoints, and custom role permissions.
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <Button
                            variant="primary"
                            onClick={() => onNavigate('blogs')}
                            icon={ArrowUpRight}
                        >
                            Manage Blogs
                        </Button>
                        <Button
                            variant="secondary"
                            onClick={() => onNavigate('users')}
                        >
                            User Accounts
                        </Button>
                    </div>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="stats-grid">
                {statItems.map((item) => (
                    <div
                        key={item.title}
                        onClick={() => onNavigate(item.resource)}
                        style={{ cursor: 'pointer' }}
                    >
                        <StatCard
                            title={item.title}
                            value={isLoading ? '…' : item.value}
                            icon={item.icon}
                        />
                    </div>
                ))}
            </div>

            {/* Architecture & System Status Card */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
                <Card>
                    <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <CheckCircle size={18} style={{ color: 'var(--success)' }} />
                        <span>System Architecture</span>
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-secondary">Backend Framework</span>
                            <strong className="text-primary">Python 3.11 + Django 5.2</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-secondary">API Layer</span>
                            <strong className="text-primary">Django REST Framework 3.18</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-secondary">Frontend Engine</span>
                            <strong className="text-primary">React 19 + Vite</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                            <span className="text-secondary">Authentication</span>
                            <strong className="text-primary">Token Auth + Admin Role Check</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span className="text-secondary">Total CMS Models</span>
                            <strong className="text-primary">25 Fully Operational</strong>
                        </div>
                    </div>
                </Card>

                <Card>
                    <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <Settings size={18} style={{ color: 'var(--secondary)' }} />
                        <span>Quick Configuration</span>
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
                        Update site branding, payment gateways, SMS gateways, and global navigation menus directly from their dedicated settings screens.
                    </p>
                    <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
                        <Button variant="secondary" size="sm" onClick={() => onNavigate('site-settings')}>
                            Site Settings
                        </Button>
                        <Button variant="secondary" size="sm" onClick={() => onNavigate('payment-gateway-settings')}>
                            Payment Gateways
                        </Button>
                        <Button variant="secondary" size="sm" onClick={() => onNavigate('menus')}>
                            Navigation Menus
                        </Button>
                        <Button variant="secondary" size="sm" onClick={() => onNavigate('sliders')}>
                            Hero Sliders
                        </Button>
                    </div>
                </Card>
            </div>
        </div>
    );
};
