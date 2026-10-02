import React from 'react';
import {
    LayoutDashboard, Users, BookOpen, Layers, FileText, Bell,
    Newspaper, Image, Images, Film, Sliders, ListOrdered,
    Briefcase, UserCheck, HeartHandshake, Download, Mail,
    HelpCircle, MessageSquare, Menu as MenuIcon, ExternalLink,
    Settings, CreditCard, Send, ShieldCheck, Search, Activity, UserCog
} from 'lucide-react';

export const navigationGroups = [
    {
        title: 'Core Administration',
        items: [
            { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard, path: '/dashboard' },
            { id: 'detector-dashboard', label: 'TruthLens Hub', icon: Activity, path: '/detector-dashboard' },
            { id: 'detector', label: 'Public Detector', icon: Search, path: '/detector' },
            { id: 'users', label: 'User Accounts', icon: Users, path: '/users' },
            { id: 'profile', label: 'Edit Admin Profile', icon: UserCog, path: '/profile' },
        ]
    },
    {
        title: 'Content & Editorial',
        items: [
            { id: 'blogs', label: 'Blogs', icon: BookOpen, resource: 'blogs' },
            { id: 'blog-categories', label: 'Blog Categories', icon: Layers, resource: 'blog-categories' },
            { id: 'pages', label: 'Pages', icon: FileText, resource: 'pages' },
            { id: 'notices', label: 'Notices', icon: Bell, resource: 'notices' },
            { id: 'news-and-updates', label: 'News & Updates', icon: Newspaper, resource: 'news-and-updates' },
        ]
    },
    {
        title: 'Media & Galleries',
        items: [
            { id: 'albums', label: 'Albums', icon: Image, resource: 'albums' },
            { id: 'album-values', label: 'Album Assets', icon: Images, resource: 'album-values' },
            { id: 'media', label: 'Media Library', icon: Film, resource: 'media' },
            { id: 'sliders', label: 'Sliders', icon: Sliders, resource: 'sliders' },
            { id: 'slider-types', label: 'Slider Types', icon: ListOrdered, resource: 'slider-types' },
        ]
    },
    {
        title: 'Organization & Careers',
        items: [
            { id: 'teams', label: 'Team Members', icon: Users, resource: 'teams' },
            { id: 'services', label: 'Services', icon: HeartHandshake, resource: 'services' },
            { id: 'careers', label: 'Careers', icon: Briefcase, resource: 'careers' },
            { id: 'career-applications', label: 'Applications', icon: UserCheck, resource: 'career-applications' },
            { id: 'testimonials', label: 'Testimonials', icon: MessageSquare, resource: 'testimonials' },
            { id: 'downloads', label: 'Downloads', icon: Download, resource: 'downloads' },
            { id: 'enquiries', label: 'Enquiries', icon: Mail, resource: 'enquiries' },
            { id: 'faqs', label: 'FAQs', icon: HelpCircle, resource: 'faqs' },
            { id: 'faq-categories', label: 'FAQ Categories', icon: Layers, resource: 'faq-categories' },
        ]
    },
    {
        title: 'Settings & Structure',
        items: [
            { id: 'popups', label: 'Popups', icon: ExternalLink, resource: 'popups' },
            { id: 'menus', label: 'Navigation Menus', icon: MenuIcon, resource: 'menus' },
            { id: 'menu-items', label: 'Menu Links', icon: ListOrdered, resource: 'menu-items' },
            { id: 'site-settings', label: 'Site Settings', icon: Settings, resource: 'site-settings' },
            { id: 'payment-gateway-settings', label: 'Payment Gateways', icon: CreditCard, resource: 'payment-gateway-settings' },
            { id: 'sms-provider-settings', label: 'SMS Providers', icon: Send, resource: 'sms-provider-settings' },
        ]
    }
];

export const Sidebar = ({ activeTab, onSelectTab, isOpen }) => {
    return (
        <aside className={`app-sidebar ${isOpen ? 'open' : ''}`}>
            <div className="sidebar-header">
                <div className="brand-wrap">
                    <div className="brand-icon">
                        <ShieldCheck size={20} />
                    </div>
                    <span>Fack News Detection</span>
                </div>
            </div>

            <div className="sidebar-nav">
                {navigationGroups.map((group) => (
                    <div key={group.title} className="nav-group">
                        <div className="nav-group-title">{group.title}</div>
                        {group.items.map((item) => {
                            const Icon = item.icon;
                            const isActive = activeTab === (item.resource || item.id);
                            return (
                                <div
                                    key={item.id}
                                    className={`nav-item ${isActive ? 'active' : ''}`}
                                    onClick={() => onSelectTab(item.resource || item.id)}
                                >
                                    <Icon size={18} />
                                    <span>{item.label}</span>
                                </div>
                            );
                        })}
                    </div>
                ))}
            </div>
        </aside>
    );
};
