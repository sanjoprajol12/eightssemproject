import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';

export const ConfirmDialog = ({
    isOpen,
    onClose,
    onConfirm,
    title = 'Confirm Deletion',
    message = 'Are you sure you want to delete this record? This action cannot be undone.',
    isLoading = false
}) => {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={title}
            maxWidth="460px"
            footer={
                <>
                    <Button variant="secondary" onClick={onClose} disabled={isLoading}>
                        Cancel
                    </Button>
                    <Button variant="danger" onClick={onConfirm} isLoading={isLoading}>
                        Delete Record
                    </Button>
                </>
            }
        >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--danger-dim)',
                    color: 'var(--danger)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                }}>
                    <AlertTriangle size={22} />
                </div>
                <div>
                    <p style={{ color: 'var(--text-primary)', fontSize: '0.925rem', lineHeight: 1.5 }}>
                        {message}
                    </p>
                </div>
            </div>
        </Modal>
    );
};
