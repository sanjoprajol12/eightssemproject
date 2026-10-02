import React from 'react';
import { LogOut, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ThemeSwitcher } from '../common/ThemeSwitcher';
import { Badge } from '../common/Badge';

export const Header = ({ currentTitle, onToggleSidebar, onSelectTab }) => {
    const { user, logout } = useAuth();

    const getInitials = (name) => {
        if (!name) return 'A';
        return name
            .split(' ')
            .map((n) => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };

    return (
        <header className="app-header">
            <div className="header-left">
                <button
                    className="btn btn-ghost btn-sm btn-icon-only"
                    onClick={onToggleSidebar}
                    aria-label="Toggle Navigation"
                >
                    <Menu size={20} />
                </button>
                <div className="breadcrumbs">
                    <span>Admin</span>
                    <span>/</span>
                    <span className="current">{currentTitle || 'Dashboard'}</span>
                </div>
            </div>

            <div className="header-right">
                <ThemeSwitcher />

                {user && (
                    <div 
                        className="user-profile-badge" 
                        onClick={() => onSelectTab && onSelectTab('profile')}
                        style={{ cursor: 'pointer' }}
                        title="Edit Admin Profile"
                    >
                        <div className="user-avatar">
                            {getInitials(user.full_name || user.email)}
                        </div>
                        <span style={{ fontWeight: 600 }}>{user.full_name || user.username}</span>
                        <Badge variant="primary" dot={false}>
                            {user.user_type || 'Admin'}
                        </Badge>
                    </div>
                )}

                <button
                    className="btn btn-secondary btn-sm"
                    onClick={logout}
                    title="Log Out"
                >
                    <LogOut size={15} />
                    <span>Logout</span>
                </button>
            </div>
        </header>
    );
};
