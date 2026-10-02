import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const AdminLayout = ({ children, activeTab, onSelectTab, currentTitle }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="admin-layout">
            <Sidebar
                activeTab={activeTab}
                onSelectTab={(tab) => {
                    onSelectTab(tab);
                    setSidebarOpen(false);
                }}
                isOpen={sidebarOpen}
            />

            <div className="app-main">
                <Header
                    currentTitle={currentTitle}
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                    onSelectTab={onSelectTab}
                />
                <main className="app-content">
                    {children}
                </main>
            </div>
        </div>
    );
};
