import React from 'react';
import { Search, Plus, RefreshCw, Edit2, Trash2 } from 'lucide-react';
import { Button } from './Button';

export const DataTable = ({
    title,
    columns,
    data = [],
    isLoading = false,
    searchQuery = '',
    onSearchChange,
    onAddNew,
    onRefresh,
    onEdit,
    onDelete,
    actions = true,
    customActions,
    pagination,
    onPageChange,
}) => {
    return (
        <div className="table-wrapper">
            {/* Toolbar */}
            <div className="table-toolbar">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1 }}>
                    {onSearchChange && (
                        <div className="table-search-box">
                            <Search className="table-search-icon" size={16} />
                            <input
                                type="text"
                                placeholder={`Search ${title || 'records'}...`}
                                value={searchQuery}
                                onChange={(e) => onSearchChange(e.target.value)}
                            />
                        </div>
                    )}
                    {onRefresh && (
                        <Button
                            variant="secondary"
                            size="sm"
                            icon={RefreshCw}
                            onClick={onRefresh}
                            isLoading={isLoading}
                            title="Refresh records"
                        >
                            Refresh
                        </Button>
                    )}
                </div>

                {onAddNew && (
                    <Button
                        variant="primary"
                        size="sm"
                        icon={Plus}
                        onClick={onAddNew}
                    >
                        Create New
                    </Button>
                )}
            </div>

            {/* Table */}
            <div className="data-table-container">
                <table className="data-table">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th key={col.key || col.accessor} style={col.style}>
                                    {col.label || col.header}
                                </th>
                            ))}
                            {actions && <th style={{ width: '110px', textAlign: 'right' }}>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {isLoading ? (
                            <tr>
                                <td colSpan={columns.length + (actions ? 1 : 0)} className="table-empty">
                                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                                        <div className="spinner" style={{ color: 'var(--primary)' }} />
                                        <span>Loading records...</span>
                                    </div>
                                </td>
                            </tr>
                        ) : data.length === 0 ? (
                            <tr>
                                <td colSpan={columns.length + (actions ? 1 : 0)} className="table-empty">
                                    No records found.
                                </td>
                            </tr>
                        ) : (
                            data.map((row, idx) => (
                                <tr key={row.id || idx}>
                                    {columns.map((col) => {
                                        const val = row[col.accessor || col.key];
                                        return (
                                            <td key={col.key || col.accessor} style={col.style}>
                                                {col.render ? col.render(val, row) : (val !== null && val !== undefined ? String(val) : '—')}
                                            </td>
                                        );
                                    })}
                                    {actions && (
                                        <td style={{ textAlign: 'right' }}>
                                            <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                                                {customActions && customActions(row)}
                                                {onEdit && (
                                                    <button
                                                        className="btn btn-ghost btn-sm btn-icon-only"
                                                        onClick={() => onEdit(row)}
                                                        title="Edit record"
                                                    >
                                                        <Edit2 size={15} style={{ color: 'var(--primary)' }} />
                                                    </button>
                                                )}
                                                {onDelete && (
                                                    <button
                                                        className="btn btn-ghost btn-sm btn-icon-only"
                                                        onClick={() => onDelete(row)}
                                                        title="Delete record"
                                                    >
                                                        <Trash2 size={15} style={{ color: 'var(--danger)' }} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    )}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {pagination && (
                <div className="table-pagination">
                    <div>
                        Showing page {pagination.currentPage || 1} of {pagination.totalPages || 1} ({pagination.totalCount || data.length} total records)
                    </div>
                    <div className="pagination-controls">
                        <Button
                            variant="secondary"
                            size="sm"
                            disabled={pagination.currentPage <= 1 || isLoading}
                            onClick={() => onPageChange && onPageChange(pagination.currentPage - 1)}
                        >
                            Previous
                        </Button>
                        <Button
                            variant="secondary"
                            size="sm"
                            disabled={pagination.currentPage >= pagination.totalPages || isLoading}
                            onClick={() => onPageChange && onPageChange(pagination.currentPage + 1)}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
};
