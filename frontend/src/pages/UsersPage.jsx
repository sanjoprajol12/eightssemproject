import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import { DataTable } from '../components/common/DataTable';
import { Modal } from '../components/common/Modal';
import { FormField } from '../components/common/FormField';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useToast } from '../components/common/Toast';

export const UsersPage = () => {
    const { showToast } = useToast();
    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [pagination, setPagination] = useState({ currentPage: 1, totalPages: 1, totalCount: 0 });

    // Modals
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [isDeleteOpen, setIsDeleteOpen] = useState(false);
    const [deletingUser, setDeletingUser] = useState(null);
    const [isSaving, setIsSaving] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        first_name: '',
        middle_name: '',
        last_name: '',
        mobile: '',
        phone: '',
        username: '',
        email: '',
        password: '',
        address: '',
        user_type: 'admin',
        access_type: 'full_access',
        is_mfa_enabled: false,
        is_email_authentication_enabled: false,
        mfa_secret_code: '',
        mfa_authentication_image: '',
        is_active: true,
    });

    const fetchUsers = useCallback(async (page = 1, search = '') => {
        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams();
            if (page) queryParams.set('page', page);
            if (search) queryParams.set('search', search);

            const res = await api.getUsers(queryParams.toString());
            setUsers(res.results || []);
            setPagination({
                currentPage: res.current_page || 1,
                totalPages: res.total_pages || 1,
                totalCount: res.count || 0
            });
        } catch (err) {
            showToast(err.message || 'Failed to fetch users', 'error');
        } finally {
            setIsLoading(false);
        }
    }, [showToast]);

    useEffect(() => {
        let isMounted = true;
        const queryParams = new URLSearchParams();
        queryParams.set('page', '1');
        if (searchQuery) queryParams.set('search', searchQuery);

        api.getUsers(queryParams.toString())
            .then(res => {
                if (!isMounted) return;
                setUsers(res.results || []);
                setPagination({
                    currentPage: res.current_page || 1,
                    totalPages: res.total_pages || 1,
                    totalCount: res.count || 0
                });
            })
            .catch(err => {
                if (isMounted) showToast(err.message || 'Failed to fetch users', 'error');
            })
            .finally(() => {
                if (isMounted) setIsLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [searchQuery, showToast]);

    const handleOpenCreate = () => {
        setEditingUser(null);
        setFormData({
            first_name: '',
            middle_name: '',
            last_name: '',
            mobile: '',
            phone: '',
            username: '',
            email: '',
            password: '',
            address: '',
            user_type: 'admin',
            access_type: 'full_access',
            is_mfa_enabled: false,
            is_email_authentication_enabled: false,
            mfa_secret_code: '',
            mfa_authentication_image: '',
            is_active: true,
        });
        setIsFormOpen(true);
    };

    const handleOpenEdit = (user) => {
        setEditingUser(user);
        setFormData({
            first_name: user.first_name || '',
            middle_name: user.middle_name || '',
            last_name: user.last_name || '',
            mobile: user.mobile || '',
            phone: user.phone || '',
            username: user.username || '',
            email: user.email || '',
            password: '', // Blank unless editing password
            address: user.address || '',
            user_type: user.user_type || 'user',
            access_type: user.access_type || '',
            is_mfa_enabled: !!user.is_mfa_enabled,
            is_email_authentication_enabled: !!user.is_email_authentication_enabled,
            mfa_secret_code: '',
            mfa_authentication_image: '',
            is_active: !!user.is_active,
        });
        setIsFormOpen(true);
    };

    const handleSaveUser = async (e) => {
        e.preventDefault();
        setIsSaving(true);

        const payload = { ...formData };
        if (!payload.password) {
            delete payload.password;
        }

        try {
            if (editingUser) {
                await api.updateUser(editingUser.id, payload);
                showToast(`User ${payload.username} updated successfully.`, 'success');
            } else {
                await api.createUser(payload);
                showToast(`User ${payload.username} created successfully.`, 'success');
            }
            setIsFormOpen(false);
            fetchUsers(pagination.currentPage, searchQuery);
        } catch (err) {
            showToast(err.message || 'Error saving user', 'error');
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteUser = async () => {
        if (!deletingUser) return;
        setIsSaving(true);
        try {
            await api.deleteUser(deletingUser.id);
            showToast(`User ${deletingUser.username} removed.`, 'success');
            setIsDeleteOpen(false);
            fetchUsers(pagination.currentPage, searchQuery);
        } catch (err) {
            showToast(err.message || 'Failed to delete user', 'error');
        } finally {
            setIsSaving(false);
        }
    };

    const columns = [
        {
            key: 'full_name',
            label: 'Name',
            render: (val, r) => (
                <div>
                    <div style={{ fontWeight: 600 }}>{val || r.username}</div>
                    <div className="text-xs text-muted">@{r.username}</div>
                </div>
            )
        },
        { key: 'email', label: 'Email' },
        { key: 'mobile', label: 'Mobile / Phone', render: (val, r) => val || r.phone || '—' },
        {
            key: 'user_type',
            label: 'Role',
            render: (val) => (
                <Badge variant={val === 'admin' ? 'primary' : 'secondary'}>
                    {val || 'user'}
                </Badge>
            )
        },
        {
            key: 'is_mfa_enabled',
            label: 'MFA',
            render: (val) => (
                <Badge variant={val ? 'success' : 'secondary'} dot={false}>
                    {val ? 'MFA Enabled' : 'Disabled'}
                </Badge>
            )
        },
        {
            key: 'is_active',
            label: 'Status',
            render: (val) => (
                <Badge variant={val ? 'success' : 'danger'}>
                    {val ? 'Active' : 'Deactivated'}
                </Badge>
            )
        },
        {
            key: 'last_logged_in',
            label: 'Last Login',
            render: (val) => val ? new Date(val).toLocaleString() : 'Never'
        },
    ];

    return (
        <div>
            <div className="page-header">
                <div className="page-header-info">
                    <h1>User Accounts</h1>
                    <p>Manage system administrators, staff members, and user access roles</p>
                </div>
            </div>

            <DataTable
                title="Users"
                columns={columns}
                data={users}
                isLoading={isLoading}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
                onRefresh={() => fetchUsers(pagination.currentPage, searchQuery)}
                onAddNew={handleOpenCreate}
                onEdit={handleOpenEdit}
                onDelete={(u) => {
                    setDeletingUser(u);
                    setIsDeleteOpen(true);
                }}
                pagination={pagination}
                onPageChange={(page) => fetchUsers(page, searchQuery)}
            />

            {/* Create / Edit Modal */}
            <Modal
                isOpen={isFormOpen}
                onClose={() => setIsFormOpen(false)}
                title={editingUser ? `Edit User: ${editingUser.username}` : 'Create New User'}
                maxWidth="680px"
                footer={
                    <>
                        <Button variant="secondary" onClick={() => setIsFormOpen(false)} disabled={isSaving}>
                            Cancel
                        </Button>
                        <Button variant="primary" onClick={handleSaveUser} isLoading={isSaving}>
                            {editingUser ? 'Save Changes' : 'Create User'}
                        </Button>
                    </>
                }
            >
                <form onSubmit={handleSaveUser}>
                    <div className="form-grid">
                        <FormField
                            label="First Name"
                            name="first_name"
                            value={formData.first_name}
                            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                            required
                        />
                        <FormField
                            label="Middle Name"
                            name="middle_name"
                            value={formData.middle_name}
                            onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
                        />
                        <FormField
                            label="Last Name"
                            name="last_name"
                            value={formData.last_name}
                            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                            required
                        />
                    </div>

                    <div className="form-grid">
                        <FormField
                            label="Username"
                            name="username"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            required
                        />
                        <FormField
                            label="Email Address"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                        />
                        <FormField
                            label={editingUser ? 'Password (leave blank to keep current)' : 'Password *'}
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            required={!editingUser}
                        />
                    </div>

                    <div className="form-grid">
                        <FormField
                            label="Mobile Number"
                            name="mobile"
                            value={formData.mobile}
                            onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                        />
                        <FormField
                            label="Phone Number"
                            name="phone"
                            value={formData.phone}
                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        />
                    </div>

                    <FormField
                        label="Address"
                        name="address"
                        type="textarea"
                        rows={2}
                        value={formData.address}
                        onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    />

                    <div className="form-grid">
                        <FormField
                            label="User Type"
                            name="user_type"
                            type="select"
                            value={formData.user_type}
                            onChange={(e) => setFormData({ ...formData, user_type: e.target.value })}
                            options={[
                                { value: 'admin', label: 'Administrator' },
                                { value: 'staff', label: 'Staff Member' },
                                { value: 'user', label: 'General User' },
                            ]}
                        />
                        <FormField
                            label="Access Type"
                            name="access_type"
                            value={formData.access_type}
                            onChange={(e) => setFormData({ ...formData, access_type: e.target.value })}
                            placeholder="e.g. full_access, editor, viewer"
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', marginTop: '0.5rem' }}>
                        <FormField
                            label="MFA Enabled"
                            name="is_mfa_enabled"
                            type="checkbox"
                            value={formData.is_mfa_enabled}
                            onChange={(e) => setFormData({ ...formData, is_mfa_enabled: e.target.value })}
                        />
                        <FormField
                            label="Email 2FA Enabled"
                            name="is_email_authentication_enabled"
                            type="checkbox"
                            value={formData.is_email_authentication_enabled}
                            onChange={(e) => setFormData({ ...formData, is_email_authentication_enabled: e.target.value })}
                        />
                        <FormField
                            label="Account Active"
                            name="is_active"
                            type="checkbox"
                            value={formData.is_active}
                            onChange={(e) => setFormData({ ...formData, is_active: e.target.value })}
                        />
                    </div>
                </form>
            </Modal>

            {/* Confirm Delete */}
            <ConfirmDialog
                isOpen={isDeleteOpen}
                onClose={() => setIsDeleteOpen(false)}
                onConfirm={handleDeleteUser}
                title="Delete User Account"
                message={`Are you sure you want to delete ${deletingUser?.email}? They will immediately lose system access.`}
                isLoading={isSaving}
            />
        </div>
    );
};
