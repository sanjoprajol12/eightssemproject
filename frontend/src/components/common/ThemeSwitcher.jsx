import React, { useState, useRef, useEffect } from 'react';
import { Moon, Sun, Zap, Check } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export const ThemeSwitcher = () => {
    const { theme, setTheme } = useTheme();
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    }, []);

    const themes = [
        { id: 'dark', label: 'Dark Mode', icon: Moon },
        { id: 'light', label: 'Light Mode', icon: Sun },
        { id: 'cyberpunk', label: 'Cyberpunk', icon: Zap },
    ];

    const currentTheme = themes.find((t) => t.id === theme) || themes[0];
    const CurrentIcon = currentTheme.icon;

    return (
        <div className="theme-switch-container" ref={containerRef}>
            <button
                className="theme-switch-trigger"
                onClick={() => setIsOpen(!isOpen)}
                aria-label="Switch Theme"
            >
                <CurrentIcon size={14} />
                <span>{currentTheme.label}</span>
            </button>

            {isOpen && (
                <div className="theme-menu">
                    {themes.map((t) => {
                        const Icon = t.icon;
                        const isSelected = theme === t.id;
                        return (
                            <div
                                key={t.id}
                                className="theme-option-item"
                                onClick={() => {
                                    setTheme(t.id);
                                    setIsOpen(false);
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <Icon size={14} />
                                    <span>{t.label}</span>
                                </div>
                                {isSelected && <Check size={14} style={{ color: 'var(--primary)' }} />}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};
