import React from 'react';
import { Badge } from '../components/common/Badge';

export const cmsModules = {
    blogs: {
        title: 'Blogs',
        singular: 'Blog',
        resource: 'blogs',
        description: 'Publish and manage editorial blog posts with SEO metadata',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'category_title', label: 'Category' },
            { key: 'publish_date', label: 'Publish Date', render: (val) => val ? new Date(val).toLocaleDateString() : 'Draft' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Published' : 'Inactive'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Title', type: 'text', required: true },
            { name: 'description', label: 'Content / Description', type: 'textarea', rows: 5 },
            { name: 'keywords', label: 'Keywords', type: 'text' },
            { name: 'seo_title', label: 'SEO Title', type: 'text' },
            { name: 'seo_keywords', label: 'SEO Keywords', type: 'text' },
            { name: 'seo_description', label: 'SEO Description', type: 'textarea', rows: 2 },
            { name: 'image', label: 'Image URL or Asset Path', type: 'text' },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'blog-categories': {
        title: 'Blog Categories',
        singular: 'Category',
        resource: 'blog-categories',
        description: 'Organize blog posts into structured topics',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'slug', label: 'Slug' },
            { key: 'position', label: 'Position' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Category Title', type: 'text', required: true },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    albums: {
        title: 'Albums',
        singular: 'Album',
        resource: 'albums',
        description: 'Photo albums and event galleries',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'event_date', label: 'Event Date' },
            { key: 'tags', label: 'Tags' },
            { key: 'position', label: 'Position' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Hidden'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Album Title', type: 'text', required: true },
            { name: 'cover_image', label: 'Cover Image URL / Path', type: 'text' },
            { name: 'event_date', label: 'Event Date', type: 'text', placeholder: 'e.g. 2026-10-02' },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'tags', label: 'Tags', type: 'text', placeholder: 'charity, youth, conference' },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'album-values': {
        title: 'Album Assets',
        singular: 'Album Asset',
        resource: 'album-values',
        description: 'Individual images and assets belonging to albums',
        columns: [
            { key: 'title', label: 'Asset Title' },
            { key: 'album_title', label: 'Album' },
            { key: 'path', label: 'File Path' },
            {
                key: 'is_featured',
                label: 'Featured',
                render: (val) => (
                    <Badge variant={val ? 'primary' : 'secondary'}>
                        {val ? 'Featured' : 'Normal'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Asset Title', type: 'text', required: true },
            { name: 'path', label: 'Asset Path / URL', type: 'text', required: true },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_featured', label: 'Is Featured Image', type: 'checkbox', default: false },
        ]
    },

    pages: {
        title: 'Pages',
        singular: 'Page',
        resource: 'pages',
        description: 'Static website pages (About Us, History, Mission, etc.)',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'slug', label: 'Slug' },
            { key: 'views', label: 'Views' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Draft'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Page Title', type: 'text', required: true },
            { name: 'content', label: 'HTML Content', type: 'textarea', rows: 6, required: true },
            { name: 'seo_title', label: 'SEO Title', type: 'text' },
            { name: 'seo_keyword', label: 'SEO Keywords', type: 'text' },
            { name: 'seo_description', label: 'SEO Description', type: 'textarea', rows: 2 },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    notices: {
        title: 'Notices',
        singular: 'Notice',
        resource: 'notices',
        description: 'Announcements and notifications broadcasted to users',
        columns: [
            { key: 'name', label: 'Notice Title' },
            { key: 'user_type', label: 'Audience' },
            { key: 'visible_from_date', label: 'Visible From', render: (val) => val ? new Date(val).toLocaleDateString() : 'Immediate' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Expired'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'name', label: 'Notice Title', type: 'text', required: true },
            { name: 'description', label: 'Notice Body', type: 'textarea', rows: 4, required: true },
            { name: 'user_type', label: 'Target Audience', type: 'select', options: ['all', 'admin', 'member', 'guest'], default: 'all' },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'news-and-updates': {
        title: 'News & Updates',
        singular: 'News Item',
        resource: 'news-and-updates',
        description: 'Press releases, news flashes, and project announcements',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'published_by', label: 'Published By' },
            { key: 'publish_date', label: 'Date', render: (val) => val ? new Date(val).toLocaleDateString() : 'Now' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Archived'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Headline', type: 'text', required: true },
            { name: 'url', label: 'External Link / Article URL', type: 'text' },
            { name: 'published_by', label: 'Author / Publisher', type: 'text' },
            { name: 'is_active', label: 'Is Published', type: 'checkbox', default: true },
        ]
    },

    media: {
        title: 'Media Library',
        singular: 'Media File',
        resource: 'media',
        description: 'Centralized document, image, and media repository',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'type', label: 'File Type' },
            { key: 'size', label: 'Size (MB)' },
            {
                key: 'is_downloadable',
                label: 'Downloadable',
                render: (val) => (
                    <Badge variant={val ? 'primary' : 'secondary'}>
                        {val ? 'Yes' : 'No'}
                    </Badge>
                )
            },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Title', type: 'text' },
            { name: 'path', label: 'Asset Path / URL', type: 'text', required: true },
            { name: 'type', label: 'Type', type: 'select', options: ['image', 'video', 'document', 'pdf', 'other'], default: 'image' },
            { name: 'size', label: 'Size in MB', type: 'number' },
            { name: 'is_downloadable', label: 'Allow Download', type: 'checkbox', default: false },
            { name: 'is_featured', label: 'Featured in Gallery', type: 'checkbox', default: false },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    sliders: {
        title: 'Sliders',
        singular: 'Slider',
        resource: 'sliders',
        description: 'Hero carousel slides and promotional banners',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'heading_text', label: 'Heading' },
            { key: 'position', label: 'Position' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Hidden'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Slider Title', type: 'text' },
            { name: 'heading_text', label: 'Hero Heading', type: 'text' },
            { name: 'sub_heading_text', label: 'Subheading', type: 'text' },
            { name: 'button_text', label: 'CTA Button Text', type: 'text' },
            { name: 'link', label: 'CTA Link', type: 'text' },
            { name: 'image', label: 'Background Image URL', type: 'text', required: true },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'show_button', label: 'Show CTA Button', type: 'checkbox', default: true },
            { name: 'new_tab', label: 'Open in New Tab', type: 'checkbox', default: false },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'slider-types': {
        title: 'Slider Types',
        singular: 'Slider Type',
        resource: 'slider-types',
        description: 'Carousel display configurations and slide groups',
        columns: [
            { key: 'title', label: 'Type Name' },
            { key: 'slug', label: 'Slug' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Slider Type Name', type: 'text', required: true },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    teams: {
        title: 'Team Members',
        singular: 'Team Member',
        resource: 'teams',
        description: 'Executive committee, board members, and volunteers',
        columns: [
            { key: 'name', label: 'Name' },
            { key: 'role', label: 'Role / Designation' },
            { key: 'type', label: 'Department' },
            { key: 'email', label: 'Email' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Inactive'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'name', label: 'Full Name', type: 'text', required: true },
            { name: 'role', label: 'Role / Title', type: 'text', placeholder: 'e.g. Club President' },
            { name: 'type', label: 'Group / Category', type: 'text', placeholder: 'Executive, Board, Volunteer' },
            { name: 'email', label: 'Email Address', type: 'email' },
            { name: 'contact_number', label: 'Phone Number', type: 'text' },
            { name: 'whatsapp_number', label: 'WhatsApp', type: 'text' },
            { name: 'fb_url', label: 'Facebook URL', type: 'text' },
            { name: 'linked_url', label: 'LinkedIn URL', type: 'text' },
            { name: 'image', label: 'Profile Photo URL', type: 'text' },
            { name: 'description', label: 'Bio / Note', type: 'textarea' },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    services: {
        title: 'Services',
        singular: 'Service',
        resource: 'services',
        description: 'Community initiatives and health/social services',
        columns: [
            { key: 'title', label: 'Service Name' },
            { key: 'type', label: 'Category' },
            { key: 'price', label: 'Cost', render: (val) => val ? `$${val}` : 'Free' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Inactive'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Service Title', type: 'text', required: true },
            { name: 'type', label: 'Service Category', type: 'text' },
            { name: 'price', label: 'Fee / Price (if applicable)', type: 'number' },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    careers: {
        title: 'Careers',
        singular: 'Career Opening',
        resource: 'careers',
        description: 'Job postings, volunteering openings, and internships',
        columns: [
            { key: 'title', label: 'Job Title' },
            { key: 'employment_type', label: 'Type' },
            { key: 'no_of_vacancies', label: 'Openings' },
            { key: 'expiry_date', label: 'Deadline', render: (val) => val || 'Open' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Closed'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Job Title', type: 'text', required: true },
            { name: 'employment_type', label: 'Employment Type', type: 'select', options: ['Full-time', 'Part-time', 'Volunteer', 'Contract', 'Internship'] },
            { name: 'no_of_vacancies', label: 'Vacancies', type: 'number', default: 1 },
            { name: 'salary_offer', label: 'Salary / Stipend', type: 'number' },
            { name: 'min_qualification', label: 'Minimum Qualification', type: 'text' },
            { name: 'opened_at', label: 'Opening Date', type: 'date' },
            { name: 'expiry_date', label: 'Deadline Date', type: 'date' },
            { name: 'description', label: 'Job Description', type: 'textarea', rows: 4 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'career-applications': {
        title: 'Career Applications',
        singular: 'Application',
        resource: 'career-applications',
        description: 'Submissions and resumes received for career openings',
        columns: [
            { key: 'first_name', label: 'Applicant Name', render: (val, r) => `${r.first_name || ''} ${r.last_name || ''}`.trim() || '—' },
            { key: 'career_title', label: 'Position' },
            { key: 'email', label: 'Email' },
            { key: 'phone', label: 'Phone' },
            {
                key: 'is_shortlisted',
                label: 'Shortlisted',
                render: (val) => (
                    <Badge variant={val === '1' || val === true ? 'success' : 'secondary'}>
                        {val === '1' || val === true ? 'Shortlisted' : 'Under Review'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'first_name', label: 'First Name', type: 'text', required: true },
            { name: 'last_name', label: 'Last Name', type: 'text' },
            { name: 'email', label: 'Email', type: 'email', required: true },
            { name: 'phone', label: 'Phone Number', type: 'text' },
            { name: 'file', label: 'Resume File Path / URL', type: 'text' },
            { name: 'is_read', label: 'Mark as Read', type: 'select', options: [{ value: '0', label: 'Unread' }, { value: '1', label: 'Read' }] },
            { name: 'is_shortlisted', label: 'Shortlist Candidate', type: 'select', options: [{ value: '0', label: 'No' }, { value: '1', label: 'Yes' }] },
        ]
    },

    testimonials: {
        title: 'Testimonials',
        singular: 'Testimonial',
        resource: 'testimonials',
        description: 'Endorsements, community feedback, and reviews',
        columns: [
            { key: 'name', label: 'Name' },
            { key: 'rating', label: 'Rating', render: (val) => '⭐'.repeat(val || 5) },
            { key: 'type', label: 'Role / Designation' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Visible' : 'Hidden'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'name', label: 'Person Name', type: 'text', required: true },
            { name: 'type', label: 'Designation / Organization', type: 'text' },
            { name: 'rating', label: 'Rating (1 - 5)', type: 'select', options: [1, 2, 3, 4, 5], default: 5 },
            { name: 'description', label: 'Testimonial Quote', type: 'textarea', rows: 3, required: true },
            { name: 'image', label: 'Avatar / Photo URL', type: 'text' },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    downloads: {
        title: 'Downloads',
        singular: 'Download File',
        resource: 'downloads',
        description: 'Public forms, club charters, reports, and bylaws',
        columns: [
            { key: 'title', label: 'Title' },
            {
                key: 'is_private',
                label: 'Access',
                render: (val) => (
                    <Badge variant={val ? 'warning' : 'info'}>
                        {val ? 'Members Only' : 'Public'}
                    </Badge>
                )
            },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Document Title', type: 'text', required: true },
            { name: 'file_path', label: 'Download URL / File Path', type: 'text', required: true },
            { name: 'preview_image', label: 'Cover Thumbnail', type: 'text' },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'is_private', label: 'Members Only (Private)', type: 'checkbox', default: false },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    enquiries: {
        title: 'Enquiries',
        singular: 'Enquiry',
        resource: 'enquiries',
        description: 'Messages and inquiries submitted via contact forms',
        columns: [
            { key: 'name', label: 'Name' },
            { key: 'email', label: 'Email' },
            { key: 'subject', label: 'Subject' },
            {
                key: 'mark_as_read',
                label: 'Read Status',
                render: (val) => (
                    <Badge variant={val ? 'secondary' : 'warning'}>
                        {val ? 'Read' : 'New'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'name', label: 'Sender Name', type: 'text', required: true },
            { name: 'email', label: 'Sender Email', type: 'email', required: true },
            { name: 'phone', label: 'Phone Number', type: 'text' },
            { name: 'subject', label: 'Subject', type: 'text', required: true },
            { name: 'message', label: 'Message Body', type: 'textarea', rows: 4, required: true },
            { name: 'mark_as_read', label: 'Mark as Processed / Read', type: 'checkbox' },
        ]
    },

    faqs: {
        title: 'FAQs',
        singular: 'FAQ',
        resource: 'faqs',
        description: 'Frequently asked questions and answers',
        columns: [
            { key: 'title', label: 'Question' },
            { key: 'category_name', label: 'Category' },
            { key: 'position', label: 'Position' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Hidden'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Question', type: 'text', required: true },
            { name: 'description', label: 'Answer Body', type: 'textarea', rows: 4, required: true },
            { name: 'position', label: 'Display Order', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'faq-categories': {
        title: 'FAQ Categories',
        singular: 'FAQ Category',
        resource: 'faq-categories',
        description: 'Topic groupings for FAQs',
        columns: [
            { key: 'name', label: 'Category Name' },
            { key: 'slug', label: 'Slug' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'name', label: 'Category Name', type: 'text', required: true },
            { name: 'description', label: 'Description', type: 'textarea' },
            { name: 'type', label: 'Type Tag', type: 'text' },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    popups: {
        title: 'Popups',
        singular: 'Popup Modal',
        resource: 'popups',
        description: 'Promotional modal alerts and banners on homepage',
        columns: [
            { key: 'title', label: 'Title' },
            { key: 'type', label: 'Type' },
            { key: 'start_date', label: 'Start', render: (val) => val ? new Date(val).toLocaleDateString() : 'Immediate' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Popup Title', type: 'text' },
            { name: 'type', label: 'Popup Type', type: 'select', options: ['image', 'video', 'announcement', 'event'] },
            { name: 'image', label: 'Banner Image URL', type: 'text' },
            { name: 'video_url', label: 'Video Embed URL', type: 'text' },
            { name: 'link', label: 'Call to Action URL', type: 'text' },
            { name: 'description', label: 'Popup Message', type: 'textarea' },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    menus: {
        title: 'Navigation Menus',
        singular: 'Menu',
        resource: 'menus',
        description: 'Header, footer, and sidebar navigation menus',
        columns: [
            { key: 'title', label: 'Menu Title' },
            { key: 'menu_type', label: 'Type' },
            {
                key: 'header',
                label: 'Header Nav',
                render: (val) => (
                    <Badge variant={val ? 'primary' : 'secondary'}>
                        {val ? 'Header' : 'Footer'}
                    </Badge>
                )
            },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Menu Name', type: 'text', required: true },
            { name: 'menu_type', label: 'Placement Type', type: 'select', options: ['header', 'footer', 'sidebar'] },
            { name: 'header', label: 'Display in Main Header', type: 'checkbox', default: false },
            { name: 'position', label: 'Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'menu-items': {
        title: 'Menu Items',
        singular: 'Menu Item',
        resource: 'menu-items',
        description: 'Individual links inside navigation menus',
        columns: [
            { key: 'title', label: 'Link Title' },
            { key: 'menu_title', label: 'Parent Menu' },
            { key: 'link', label: 'URL' },
            { key: 'position', label: 'Order' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Hidden'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Link Text', type: 'text', required: true },
            { name: 'link', label: 'Destination URL', type: 'text', placeholder: '/about-us or https://...' },
            { name: 'type', label: 'Link Type', type: 'select', options: ['internal', 'external', 'page', 'blog'] },
            { name: 'new_tab', label: 'Open in New Tab', type: 'checkbox', default: false },
            { name: 'display_on_website', label: 'Display on Website', type: 'checkbox', default: true },
            { name: 'position', label: 'Sort Position', type: 'number', default: 0 },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'site-settings': {
        title: 'Site Settings',
        singular: 'Site Setting',
        resource: 'site-settings',
        description: 'Branding, social handles, tracking codes, and club config',
        columns: [
            { key: 'company_name', label: 'Company / Organization' },
            { key: 'email', label: 'Email' },
            { key: 'phone', label: 'Phone' },
            { key: 'website', label: 'Website' },
        ],
        fields: [
            { name: 'company_name', label: 'Organization Name', type: 'text', required: true },
            { name: 'slogan', label: 'Slogan', type: 'text' },
            { name: 'tagline', label: 'Tagline', type: 'text' },
            { name: 'website', label: 'Website URL', type: 'text' },
            { name: 'email', label: 'Contact Email', type: 'email' },
            { name: 'mobile', label: 'Mobile Number', type: 'text' },
            { name: 'phone', label: 'Phone Number', type: 'text' },
            { name: 'address', label: 'Physical Address', type: 'textarea', rows: 2 },
            { name: 'facebook', label: 'Facebook URL', type: 'text' },
            { name: 'instagram', label: 'Instagram URL', type: 'text' },
            { name: 'twitter', label: 'Twitter URL', type: 'text' },
            { name: 'youtube', label: 'YouTube URL', type: 'text' },
            { name: 'linkedin', label: 'LinkedIn URL', type: 'text' },
            { name: 'whatsapp', label: 'WhatsApp Number', type: 'text' },
            { name: 'copy_right_text', label: 'Copyright Notice', type: 'text' },
            { name: 'logo', label: 'Logo Image URL', type: 'text' },
            { name: 'fav_icon', label: 'Favicon URL', type: 'text' },
            { name: 'enable_cookies', label: 'Enable Cookie Consent Banner', type: 'checkbox' },
        ]
    },

    'payment-gateway-settings': {
        title: 'Payment Gateways',
        singular: 'Payment Gateway',
        resource: 'payment-gateway-settings',
        description: 'Payment processors, donation gateways, and bank QR codes',
        columns: [
            { key: 'title', label: 'Gateway Name' },
            { key: 'type', label: 'Provider Type' },
            { key: 'merchant_id', label: 'Merchant ID' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Enabled' : 'Disabled'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Gateway Title', type: 'text', required: true },
            { name: 'type', label: 'Provider Type', type: 'select', options: ['stripe', 'paypal', 'esewa', 'khalti', 'fonepay', 'bank_transfer', 'other'] },
            { name: 'merchant_id', label: 'Merchant Code / ID', type: 'text' },
            { name: 'public_key', label: 'Public Key / Client ID', type: 'text' },
            { name: 'private_key', label: 'Secret Key', type: 'text' },
            { name: 'app_id', label: 'App ID', type: 'text' },
            { name: 'bank_qr_code', label: 'Bank QR Image URL', type: 'text' },
            { name: 'description', label: 'Instructions for Donors', type: 'textarea' },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    },

    'sms-provider-settings': {
        title: 'SMS Providers',
        singular: 'SMS Provider',
        resource: 'sms-provider-settings',
        description: 'SMS gateways for notifications and 2FA authentication',
        columns: [
            { key: 'title', label: 'Provider Name' },
            { key: 'type', label: 'Type' },
            { key: 'sender', label: 'Sender ID' },
            {
                key: 'is_active',
                label: 'Status',
                render: (val) => (
                    <Badge variant={val ? 'success' : 'danger'}>
                        {val ? 'Active' : 'Inactive'}
                    </Badge>
                )
            }
        ],
        fields: [
            { name: 'title', label: 'Provider Name', type: 'text', required: true },
            { name: 'type', label: 'Provider Type', type: 'select', options: ['twilio', 'sparrow_sms', 'infobip', 'custom'] },
            { name: 'sender', label: 'Sender Header / Phone', type: 'text' },
            { name: 'token', label: 'API Token / Auth Secret', type: 'text' },
            { name: 'is_active', label: 'Is Active', type: 'checkbox', default: true },
        ]
    }
};
