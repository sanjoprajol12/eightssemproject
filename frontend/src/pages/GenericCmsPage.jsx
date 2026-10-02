import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { cmsModules } from '../config/cmsModules';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import { FormField } from '../components/common/FormField';
import { Button } from '../components/common/Button';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useToast } from '../components/common/Toast';

export const GenericCmsPage = ({ resourceKey }) => {
    const { showToast } = useToast();
    const config = cmsModules[resourceKey] || {
        title: resourceKey,
        singular: resourceKey,
        resource: resourceKey,
        columns: [{ key: 'id', label: 'ID' }, { key: 'title', label: 'Title' }],
        fields: [{ name: 'title', label: 'Title', type: 'text', required: true }]
    };

    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [pagination, setPagination] = useState({ currentPage: 1, totalPages: 1, totalCount: 0 });

    // Modals
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingItem, setEditingItem] = useState(null);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [deletingItem, setDeletingItem] = useState(null);
    const [isSaving, setIsSaving] = useState(false);

    // Dynamic Form Data state
    const [formData, setFormData] = useState({});

    const fetchData = useCallback(async (page = 1, search = '') => {
        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams();
            if (page) queryParams.set('page', page);
            if (search) queryParams.set('search', search);

            const res = await api.list(config.resource, queryParams.toString());
            setData(res.results || []);
            setPagination({
                currentPage: res.current_page || 1,
                totalPages: res.total_pages || 1,
                totalCount: res.count || 0
            });
        } catch (err) {
            showToast(err.message || `Failed to fetch ${config.title}`, 'error');
        } finally {
            setIsLoading(false);
        }
    }, [config.resource, config.title, showToast]);

    useEffect(() => {
        let isMounted = true;
        const queryParams = new URLSearchParams();
        queryParams.set('page', '1');
        if (searchQuery) queryParams.set('search', searchQuery);

        api.list(config.resource, queryParams.toString())
            .then(res => {
                if (!isMounted) return;
                setData(res.results || []);
                setPagination({
                    currentPage: res.current_page || 1,
                    totalPages: res.total_pages || 1,
                    totalCount: res.count || 0
                });
            })
            .catch(err => {
                if (isMounted) showToast(err.message || `Failed to fetch ${config.title}`, 'error');
            })
            .finally(() => {
                if (isMounted) setIsLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [config.resource, config.title, searchQuery, showToast]);

    const handleOpenCreate = () => {
        setEditingItem(null);
        const initial = {};
        (config.fields || []).forEach((field) => {
            initial[field.name] = field.default !== undefined ? field.default : (field.type === 'checkbox' ? false : '');
        });
        setFormData(initial);
        setIsFormOpen(true);
    };

    const handleOpenEdit = (item) => {
        setEditingItem(item);
        const initial = {};
        (config.fields || []).forEach((field) => {
            initial[field.name] = item[field.name] !== undefined ? item[field.name] : (field.type === 'checkbox' ? false : '');
        });
        setFormData(initial);
        setIsFormOpen(true);
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setIsSaving(true);

        try {
            if (editingItem) {
                await api.update(config.resource, editingItem.id, formData);
                showToast(`${config.singular} updated successfully.`, 'success');
            } else {
                await api.create(config.resource, formData);
                showToast(`${config.singular} created successfully.`, 'success');
            }
            setIsFormOpen(false);
            fetchData(pagination.currentPage, searchQuery);
        } catch (err) {
            showToast(err.message || 'Error saving record', 'error');
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!deletingItem) return;
        setIsSaving(true);
        try {
            await api.delete(config.resource, deletingItem.id);
            showToast(`${config.singular} removed successfully.`, 'success');
            setIsDeleteOpen(false);
            fetchData(pagination.currentPage, searchQuery);
        } catch (err) {
            showToast(err.message || 'Failed to delete record', 'error');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <div className="page-header-info">
                    <h1>{config.title}</h1>
                    {config.description && <p>{config.description}</p>}
                </div>
            </div>

            <DataTable
                title={config.title}
                columns={config.columns}
                data={data}
                isLoading={isLoading}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                onRefresh={() => fetchData(pagination.currentPage, searchQuery)}
                onAddNew={handleOpenCreate}
                onEdit={handleOpenEdit}
                onDelete={(item) => {
                    setDeletingItem(item);
                    setIsDeleteOpen(true);
                }}
                pagination={pagination}
                onPageChange={(page) => fetchData(page, searchQuery)}
            />

            {/* Create & Edit Modal */}
            <Modal
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                title={editingItem ? `Edit ${config.singular}` : `Create ${config.singular}`}
                maxWidth="640px"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setIsFormOpen(false)} disabled={isSaving}>
                            Cancel
                        </Button>
                        <Button variant="primary" onClick={handleSave} isLoading={isSaving}>
                            {editingItem ? 'Save Changes' : 'Create Record'}
                        </Button>
                    </>
                }
            >
                <form onSubmit={handleSave}>
                    {(config.fields || []).map((field) => (
                        <FormField
                            key={field.name}
                            label={field.label}
                            name={field.name}
                            type={field.type || 'text'}
                            value={formData[field.name]}
                            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                            placeholder={field.placeholder || ''}
                            required={field.required}
                            options={field.options}
                            rows={field.rows || 3}
                        />
                    ))}
                </form>
            </Modal>

            {/* Confirm Delete */}
            <ConfirmDialog
                isOpen={isDeleteOpen}
                onClose={() => setIsDeleteOpen(false)}
                onConfirm={handleDelete}
                title={`Delete ${config.singular}`}
                message={`Are you sure you want to remove this ${config.singular.toLowerCase()}? This action can be soft-restored by system admins.`}
                isLoading={isSaving}
            />
        </div>
    );
};
