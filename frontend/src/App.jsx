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
import { Dashboard } from './pages/Dashboard';
import { UsersPage } from './pages/UsersPage';
import { GenericCmsPage } from './pages/GenericCmsPage';
import { cmsModules } from './config/cmsModules';

const MainApp = () => {
    const { isAuthenticated, isLoading } = useAuth();
    const [publicView, setPublicView] = useState('detector'); // 'detector' | 'login' | 'register'
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

    // Unauthenticated routes: Detector, Login, Register
    if (!isAuthenticated) {
        if (publicView === 'login') {
            return (
                <Login
                    onNavigateToRegister={() => setPublicView('register')}
                    onNavigateToDetector={() => setPublicView('detector')}
                />
            );
        }

        if (publicView === 'register') {
            return (
                <RegisterPage
                    onNavigateToLogin={() => setPublicView('login')}
                    onNavigateToDetector={() => setPublicView('detector')}
                />
            );
        }

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

    // Authenticated admin routing
    const getTitle = () => {
        if (activeTab === 'dashboard') return 'Dashboard Overview';
        if (activeTab === 'detector-dashboard') return 'TruthLens Hub';
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
            {activeTab === 'detector-dashboard' && <DetectorDashboardPage />}
            {activeTab === 'detector' && (
                <DetectorPage onNavigate={(dest) => setActiveTab(dest === 'login' ? 'dashboard' : dest)} />
            )}
            {activeTab === 'profile' && (
                <AdminEditPage onBackToDashboard={() => setActiveTab('dashboard')} />
            )}
            {activeTab === 'users' && <UsersPage />}
            {activeTab !== 'dashboard' &&
             activeTab !== 'detector-dashboard' &&
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
