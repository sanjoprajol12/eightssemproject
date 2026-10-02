import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

const ToastContext = createContext();

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const showToast = useCallback((message, type = 'info', duration = 3500) => {
        const id = Date.now() + Math.random();
        setToasts((prev) => [...prev, { id, message, type }]);

        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id));
        }, duration);
    }, []);

    const removeToast = (id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    };

    return (
        <ToastContext.Provider value={{ showToast, addToast: showToast }}>
            {children}
            <div className="toast-container">
                {toasts.map((toast) => {
                    const Icon = toast.type === 'success' ? CheckCircle2 : toast.type === 'error' ? AlertCircle : Info;
                    return (
                        <div key={toast.id} className={`toast-item ${toast.type}`}>
                            <Icon size={18} style={{ flexShrink: 0 }} />
                            <span style={{ flex: 1 }}>{toast.message}</span>
                            <button
                                className="btn btn-ghost btn-sm btn-icon-only"
                                onClick={() => removeToast(toast.id)}
                            >
                                <X size={14} />
                            </button>
                        </div>
                    );
                })}
            </div>
        </ToastContext.Provider>
    );
};

export const useToast = () => useContext(ToastContext);
