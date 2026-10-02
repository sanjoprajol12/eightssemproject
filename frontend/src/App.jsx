import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './components/common/Toast';
import { AdminLayout } from './components/layout/AdminLayout';
import { Login } from './pages/Login';
import { RegisterPage } from './pages/RegisterPage';
import { AdminEditPage } from './pages/AdminEditPage';
import { DetectorPage } from './pages/DetectorPage';
import { DetectorDashboardPage } from './pages/DetectorDashboardPage';
import { TotalModelsPage } from './pages/TotalModelsPage';
import { Dashboard } from './pages/Dashboard';
import { UsersPage } from './pages/UsersPage';
import { GenericCmsPage } from './pages/GenericCmsPage';
import { cmsModules } from './config/cmsModules';

const MainApp = () => {
    const { isAuthenticated, isLoading } = useAuth();

    // Host & Path domain detection:
    // Main domain (APP_URL): 'facknews.local' -> Welcome / Detector & About
    // Admin domain (PORTAL_URL): 'portal.appur' -> Login first, then Dashboard if already logged in
    const hostname = window.location.hostname.toLowerCase();
    const pathname = window.location.pathname.toLowerCase();
    const isPortalDomain = (
        hostname === 'portal.appur' ||
        hostname.startsWith('portal.') ||
        pathname === '/login' ||
        pathname === '/login/' ||
        pathname.startsWith('/portal') ||
        pathname.startsWith('/dashboard')
    );

    const [publicView, setPublicView] = useState(isPortalDomain ? 'login' : 'detector');
    const [activeTab, setActiveTab] = useState('dashboard');

    if (isLoading) {
        return (
            <div style={{
                height: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'var(--bg-app)',
                color: 'var(--text-primary)',
                gap: '0.75rem'
            }}>
                <div className="spinner" style={{ color: 'var(--primary)' }} />
                <span>Loading TruthLens Platform...</span>
            </div>
        );
    }

    // Portal Domain Routing (portal.appur / /portal / /login):
    // 1. If unauthenticated -> return Login page first
    // 2. If authenticated -> return Dashboard
    if (isPortalDomain) {
        if (!isAuthenticated) {
            if (publicView === 'register') {
                return (
                    <RegisterPage
                        onNavigateToLogin={() => setPublicView('login')}
                        onNavigateToDetector={() => {
                            window.location.href = '/';
                        }}
                    />
                );
            }
            return (
                <Login
                    onNavigateToRegister={() => setPublicView('register')}
                    onNavigateToDetector={() => {
                        window.location.href = '/';
                    }}
                />
            );
        }
        // If authenticated on portal domain, proceed to AdminLayout / Dashboard
    } else {
        // Main domain (facknews.local / public visitor):
        // Show public welcome DetectorPage with Home and About (Contact Us)
        if (!isAuthenticated) {
            return (
                <DetectorPage
                    onNavigate={(destination) => {
                        if (destination === 'login' || destination === 'dashboard') {
                            setPublicView('login');
                        }
                    }}
                />
            );
        }
    }

    // Authenticated admin layout routing
    const getTitle = () => {
        if (activeTab === 'dashboard') return 'Dashboard Overview';
        if (activeTab === 'detector-dashboard') return 'TruthLens Hub';
        if (activeTab === 'total-model') return 'Total Models & Dataset Analytics';
        if (activeTab === 'detector') return 'Fake News Detector';
        if (activeTab === 'profile') return 'Admin Profile & Settings';
        if (activeTab === 'users') return 'User Accounts';
        if (cmsModules[activeTab]) return cmsModules[activeTab].title;
        return activeTab;
    };

    return (
        <AdminLayout
            activeTab={activeTab}
            onSelectTab={setActiveTab}
            currentTitle={getTitle()}
        >
            {activeTab === 'dashboard' && <Dashboard onNavigate={setActiveTab} />}
            {activeTab === 'detector-dashboard' && <DetectorDashboardPage onNavigate={setActiveTab} />}
            {activeTab === 'total-model' && <TotalModelsPage onNavigate={setActiveTab} />}
            {activeTab === 'detector' && (
                <DetectorPage onNavigate={(dest) => setActiveTab(dest === 'login' ? 'dashboard' : dest)} />
            )}
            {activeTab === 'profile' && (
                <AdminEditPage onBackToDashboard={() => setActiveTab('dashboard')} />
            )}
            {activeTab === 'users' && <UsersPage />}
            {activeTab !== 'dashboard' &&
             activeTab !== 'detector-dashboard' &&
             activeTab !== 'total-model' &&
             activeTab !== 'detector' &&
             activeTab !== 'profile' &&
             activeTab !== 'users' && (
                <GenericCmsPage key={activeTab} resourceKey={activeTab} />
            )}
        </AdminLayout>
    );
};

export default function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <ToastProvider>
                    <MainApp />
                </ToastProvider>
            </AuthProvider>
        </ThemeProvider>
    );
}
