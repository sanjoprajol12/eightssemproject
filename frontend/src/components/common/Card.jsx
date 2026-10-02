import React from 'react';

export const Card = ({ children, className = '', hover = false, ...props }) => {
    return (
        <div
            className={`glass-card ${hover ? 'glass-card-hover' : ''} ${className}`}
            {...props}
        >
            {children}
        </div>
    );
};

export const StatCard = ({
    title,
    value,
    icon: Icon,
    subtitle,
    className = ''
}) => {
    return (
        <div className={`stat-card ${className}`}>
            {Icon && (
                <div className="stat-icon">
                    <Icon size={24} />
                </div>
            )}
            <div className="stat-info">
                <div className="stat-value">{value ?? 0}</div>
                <div className="stat-label">{title}</div>
                {subtitle && <div className="text-xs text-muted">{subtitle}</div>}
            </div>
        </div>
    );
};
