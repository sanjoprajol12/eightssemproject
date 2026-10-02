import React from 'react';

export const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    icon: Icon,
    className = '',
    disabled = false,
    ...props
}) => {
    const variantClass = `btn-${variant}`;
    const sizeClass = size === 'sm' ? 'btn-sm' : '';

    return (
        <button
            className={`btn ${variantClass} ${sizeClass} ${className}`}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <div className="spinner" />
            ) : Icon ? (
                <Icon size={16} />
            ) : null}
            <span>{children}</span>
        </button>
    );
};
