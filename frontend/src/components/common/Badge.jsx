import React from 'react';

export const Badge = ({
    children,
    variant = 'primary',
    dot = true,
    className = ''
}) => {
    return (
        <span className={`badge badge-${variant} ${className}`}>
            {dot && <span className="badge-dot" />}
            {children}
        </span>
    );
};
