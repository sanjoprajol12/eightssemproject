import React from 'react';

export const FormField = ({
    label,
    name,
    type = 'text',
    value,
    onChange,
    placeholder = '',
    required = false,
    options = [],
    rows = 3,
    error = '',
    helpText = '',
    className = '',
    ...props
}) => {
    if (type === 'checkbox') {
        return (
            <div className={`form-group ${className}`}>
                <label className="form-checkbox-label">
                    <input
                        type="checkbox"
                        name={name}
                        checked={!!value}
                        onChange={(e) => onChange({ target: { name, value: e.target.checked } })}
                        className="form-checkbox"
                        {...props}
                    />
                    <span>{label}</span>
                </label>
                {helpText && <span className="text-xs text-muted">{helpText}</span>}
            </div>
        );
    }

    if (type === 'select') {
        return (
            <div className={`form-group ${className}`}>
                {label && <label className="form-label" htmlFor={name}>{label} {required && '*'}</label>}
                <select
                    id={name}
                    name={name}
                    value={value ?? ''}
                    onChange={onChange}
                    className="form-select"
                    required={required}
                    {...props}
                >
                    <option value="">Select option...</option>
                    {options.map((opt) => (
                        <option
                            key={opt.value !== undefined ? opt.value : opt}
                            value={opt.value !== undefined ? opt.value : opt}
                        >
                            {opt.label !== undefined ? opt.label : opt}
                        </option>
                    ))}
                </select>
                {error && <span className="text-xs" style={{ color: 'var(--danger)' }}>{error}</span>}
                {helpText && <span className="text-xs text-muted">{helpText}</span>}
            </div>
        );
    }

    if (type === 'textarea') {
        return (
            <div className={`form-group ${className}`}>
                {label && <label className="form-label" htmlFor={name}>{label} {required && '*'}</label>}
                <textarea
                    id={name}
                    name={name}
                    value={value ?? ''}
                    onChange={onChange}
                    rows={rows}
                    placeholder={placeholder}
                    className="form-textarea"
                    required={required}
                    {...props}
                />
                {error && <span className="text-xs" style={{ color: 'var(--danger)' }}>{error}</span>}
                {helpText && <span className="text-xs text-muted">{helpText}</span>}
            </div>
        );
    }

    return (
        <div className={`form-group ${className}`}>
            {label && <label className="form-label" htmlFor={name}>{label} {required && '*'}</label>}
            <input
                id={name}
                type={type}
                name={name}
                value={value ?? ''}
                onChange={onChange}
                placeholder={placeholder}
                className="form-control"
                required={required}
                {...props}
            />
            {error && <span className="text-xs" style={{ color: 'var(--danger)' }}>{error}</span>}
            {helpText && <span className="text-xs text-muted">{helpText}</span>}
        </div>
    );
};
