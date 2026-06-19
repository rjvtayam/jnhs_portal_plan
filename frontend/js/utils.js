// ===== THEME SYSTEM =====
function getTheme() {
    return localStorage.getItem('jnhs_theme') || 'light';
}

function setTheme(theme) {
    localStorage.setItem('jnhs_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

function toggleTheme() {
    const current = getTheme();
    setTheme(current === 'dark' ? 'light' : 'dark');
}

// Apply theme immediately on script load
document.documentElement.setAttribute('data-theme', getTheme());

function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString('en-PH', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit',
    });
}

function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// ===== TOAST / FLASH MESSAGES =====
(function() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
})();

const _toastIcons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle',
};

function showNotification(message, type = 'success') {
    const container = document.querySelector('.toast-container') || (() => {
        const c = document.createElement('div');
        c.className = 'toast-container';
        document.body.appendChild(c);
        return c;
    })();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${_toastIcons[type] || _toastIcons.info} toast-icon"></i>
        <span class="toast-msg">${message}</span>
        <button class="toast-close" onclick="removeToast(this.parentElement)">&times;</button>
    `;
    container.appendChild(toast);
    setTimeout(() => removeToast(toast), 4000);
}

function removeToast(el) {
    if (!el || el.classList.contains('removing')) return;
    el.classList.add('removing');
    setTimeout(() => el.remove(), 300);
}

// ===== CUSTOM CONFIRM MODAL =====
function showConfirmModal(message, options = {}) {
    const {
        title = 'Confirm Delete',
        confirmText = 'Delete',
        cancelText = 'Cancel',
        type = 'danger',
        icon = type === 'danger' ? 'fa-trash-alt' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-question-circle',
    } = options;

    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';
        overlay.innerHTML = `
            <div class="confirm-box">
                <div class="confirm-icon ${type}"><i class="fas ${icon}"></i></div>
                <div class="confirm-title">${title}</div>
                <div class="confirm-message">${message}</div>
                <div class="confirm-actions">
                    <button class="confirm-btn cancel" data-action="cancel">${cancelText}</button>
                    <button class="confirm-btn ${type}" data-action="confirm">${confirmText}</button>
                </div>
            </div>
        `;

        function cleanup(result) {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 250);
            resolve(result);
        }

        overlay.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action === 'cancel' || action === undefined && e.target === overlay) cleanup(false);
            if (action === 'confirm') cleanup(true);
        });

        overlay.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') cleanup(false);
            if (e.key === 'Enter') cleanup(true);
        });

        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));
        overlay.querySelector('[data-action="cancel"]').focus();
    });
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function renderSidebar(activePage) {
    const user = Auth.getUser();
    if (!user) return '';

    const roleMenus = {
        super_admin: `
            <div class="nav-section">
                <div class="nav-section-title">System Monitoring</div>
                <a href="/pages/superadmin/dashboard.html" class="nav-item ${activePage === 'system-monitor' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-heartbeat"></i></span> System Dashboard
                </a>
                <a href="/pages/superadmin/errors.html" class="nav-item ${activePage === 'system-errors' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bug"></i></span> Error Logs
                </a>
                <a href="/pages/superadmin/activity.html" class="nav-item ${activePage === 'activity-log' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-clipboard-list"></i></span> Activity Log
                </a>
                <a href="/pages/superadmin/users.html" class="nav-item ${activePage === 'system-users' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-users-cog"></i></span> User Management
                </a>
                <a href="/pages/superadmin/notifications.html" class="nav-item ${activePage === 'superadmin-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/superadmin/messages.html" class="nav-item ${activePage === 'superadmin-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        principal: `
            <div class="nav-section">
                <div class="nav-section-title">Overview</div>
                <a href="/pages/principal/dashboard.html" class="nav-item ${activePage === 'principal-dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-chart-pie"></i></span> Dashboard
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">View Records</div>
                <a href="/pages/principal/teachers.html" class="nav-item ${activePage === 'principal-teachers' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-chalkboard-teacher"></i></span> Teachers
                </a>
                <a href="/pages/principal/students.html" class="nav-item ${activePage === 'principal-students' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-graduate"></i></span> Students
                </a>
                <a href="/pages/principal/sections.html" class="nav-item ${activePage === 'principal-sections' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-layer-group"></i></span> Sections
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/principal/announcements.html" class="nav-item ${activePage === 'principal-announcements' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bullhorn"></i></span> Announcements
                </a>
                <a href="/pages/principal/notifications.html" class="nav-item ${activePage === 'principal-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/principal/messages.html" class="nav-item ${activePage === 'principal-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        admin: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/admin/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-th-large"></i></span> Dashboard
                </a>
                <a href="/pages/admin/students.html" class="nav-item ${activePage === 'students' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-graduate"></i></span> Students
                </a>
                <a href="/pages/admin/teachers.html" class="nav-item ${activePage === 'teachers' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-chalkboard-teacher"></i></span> Teachers
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Academic</div>
                <a href="/pages/admin/enrollment.html" class="nav-item ${activePage === 'enrollment' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-plus"></i></span> Enrollment
                </a>
                <a href="/pages/admin/grades.html" class="nav-item ${activePage === 'grades' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-book-open"></i></span> Grades
                </a>
                <a href="/pages/admin/reports.html" class="nav-item ${activePage === 'reports' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-file-pdf"></i></span> Reports
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/admin/announcements.html" class="nav-item ${activePage === 'announcements' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bullhorn"></i></span> Announcements
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Accounts</div>
                <a href="/pages/admin/account-creation.html" class="nav-item ${activePage === 'admin-accounts' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-plus"></i></span> Create Teacher Account
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/admin/notifications.html" class="nav-item ${activePage === 'admin-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/admin/messages.html" class="nav-item ${activePage === 'admin-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        registrar: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/registrar/dashboard.html" class="nav-item ${activePage === 'registrar-dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-tachometer-alt"></i></span> Dashboard
                </a>
                <a href="/pages/registrar/enrollment.html" class="nav-item ${activePage === 'registrar-enrollment' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-clipboard-list"></i></span> Enrollment
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Records</div>
                <a href="/pages/registrar/students.html" class="nav-item ${activePage === 'registrar-students' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-address-book"></i></span> Student Records
                </a>
                <a href="/pages/registrar/sections.html" class="nav-item ${activePage === 'registrar-sections' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-object-group"></i></span> Sections
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Reports</div>
                <a href="/pages/registrar/reports.html" class="nav-item ${activePage === 'registrar-reports' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-file-alt"></i></span> SF9 / SF10 Reports
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Accounts</div>
                <a href="/pages/registrar/account-creation.html" class="nav-item ${activePage === 'registrar-accounts' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-plus"></i></span> Create Accounts
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/registrar/notifications.html" class="nav-item ${activePage === 'registrar-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/registrar/messages.html" class="nav-item ${activePage === 'registrar-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        teacher: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/teacher/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-home"></i></span> Dashboard
                </a>
                <a href="/pages/teacher/my-sections.html" class="nav-item ${activePage === 'sections' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-school"></i></span> My Sections
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Academic</div>
                <a href="/pages/teacher/grade-entry.html" class="nav-item ${activePage === 'grade-entry' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-edit"></i></span> Grade Entry
                </a>
                <a href="/pages/teacher/attendance.html" class="nav-item ${activePage === 'attendance' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-check-double"></i></span> Attendance
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/teacher/notifications.html" class="nav-item ${activePage === 'teacher-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/teacher/messages.html" class="nav-item ${activePage === 'teacher-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        student: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/student/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-home"></i></span> Dashboard
                </a>
                <a href="/pages/student/grades.html" class="nav-item ${activePage === 'grades' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-star"></i></span> My Grades
                </a>
                <a href="/pages/student/attendance.html" class="nav-item ${activePage === 'attendance' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-calendar-check"></i></span> My Attendance
                </a>
                <a href="/pages/student/schedule.html" class="nav-item ${activePage === 'schedule' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-clock"></i></span> Schedule
                </a>
                <a href="/pages/student/profile.html" class="nav-item ${activePage === 'profile' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-user-circle"></i></span> Profile
                </a>
                <a href="/pages/student/notifications.html" class="nav-item ${activePage === 'student-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/student/messages.html" class="nav-item ${activePage === 'student-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
        parent: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/parent/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-home"></i></span> Dashboard
                </a>
                <a href="/pages/parent/child-progress.html" class="nav-item ${activePage === 'progress' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-chart-line"></i></span> Child Progress
                </a>
                <a href="/pages/parent/announcements.html" class="nav-item ${activePage === 'announcements' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bullhorn"></i></span> Announcements
                </a>
                <a href="/pages/parent/notifications.html" class="nav-item ${activePage === 'parent-notifications' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-bell"></i></span> Notifications
                </a>
                <a href="/pages/parent/messages.html" class="nav-item ${activePage === 'parent-messages' ? 'active' : ''}">
                    <span class="icon"><i class="fas fa-envelope"></i></span> Messages
                </a>
            </div>
        `,
    };

    return `
        <div class="sidebar-header">
            <div class="logo"><img src="/assets/images/logo.png" alt="JNHS" style="width:100%;height:100%;object-fit:contain;border-radius:8px;"></div>
            <div class="school-name">Jomalig National High School</div>
        </div>
        <nav class="sidebar-nav">
            ${roleMenus[user.role] || ''}
        </nav>
        <div class="sidebar-footer">
            <div class="nav-item" onclick="Auth.logout()">
                <span class="icon"><i class="fas fa-sign-out-alt"></i></span> Logout
            </div>
        </div>
    `;
}

function initDashboard(activePage) {
    const user = Auth.getUser();
    if (!user) {
        window.location.href = '/login.html';
        return;
    }

    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.innerHTML = renderSidebar(activePage);
    }

    const userInfo = document.querySelector('.user-info');
    if (userInfo) {
        userInfo.innerHTML = `<i class="fas fa-user-circle" style="margin-right:6px;"></i>${user.username} (${capitalize(user.role)})`;
    }

    // Inject notification bell into topbar-actions
    const topbarActions = document.querySelector('.topbar-actions');
    if (topbarActions && !document.querySelector('.notif-wrapper')) {
        const rolePath = user.role === 'super_admin' ? 'superadmin' : user.role;
        const bellHtml = `
            <div class="notif-wrapper">
                <button class="notif-bell" onclick="toggleNotifPanel(event)" title="Notifications">
                    <i class="fas fa-bell"></i>
                    <span class="notif-badge" id="notifBadge" style="display:none">0</span>
                </button>
                <div class="notif-panel" id="notifPanel">
                    <div class="notif-panel-header">
                        <h4>Notifications</h4>
                        <button onclick="markAllNotifRead(event)">Mark all read</button>
                    </div>
                    <div class="notif-list" id="notifList">
                        <div class="notif-empty">No notifications yet</div>
                    </div>
                    <a href="/pages/${rolePath}/notifications.html" class="notif-view-all">View All Notifications</a>
                </div>
            </div>
            <a href="/pages/${rolePath}/messages.html" class="notif-bell" title="Messages" style="text-decoration:none;position:relative;">
                <i class="fas fa-envelope"></i>
                <span class="notif-badge" id="msgBadge" style="display:none">0</span>
            </a>
            <button class="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">
                <i class="fas ${getTheme() === 'dark' ? 'fa-sun' : 'fa-moon'}" id="themeIcon"></i>
            </button>
        `;
        topbarActions.insertAdjacentHTML('afterbegin', bellHtml);
    }

    // Apply current theme
    setTheme(getTheme());

    // Start notification + message polling
    startNotifPolling();
    fetchMsgUnreadCount();
}

// ===== NOTIFICATION SYSTEM =====

let _notifPollInterval = null;
let _notifRecentInterval = null;

function toggleNotifPanel(e) {
    if (e) e.stopPropagation();
    const panel = document.getElementById('notifPanel');
    if (!panel) return;
    const isOpen = panel.classList.contains('show');
    panel.classList.toggle('show');
    if (!isOpen) {
        fetchRecentNotifications();
        document.addEventListener('click', closeNotifPanel);
    }
}

function closeNotifPanel(e) {
    const panel = document.getElementById('notifPanel');
    const wrapper = document.querySelector('.notif-wrapper');
    if (panel && wrapper && !wrapper.contains(e.target)) {
        panel.classList.remove('show');
        document.removeEventListener('click', closeNotifPanel);
    }
}

const notifTypeIcons = {
    announcement: 'fa-bullhorn',
    grade: 'fa-star',
    enrollment: 'fa-user-plus',
    attendance: 'fa-calendar-check',
    account: 'fa-user-circle',
    message: 'fa-envelope',
    system: 'fa-cog',
};

function renderNotifItem(n) {
    const icon = notifTypeIcons[n.type] || 'fa-bell';
    const timeAgo = getTimeAgo(n.created_at);
    return `
        <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="handleNotifClick(${n.id}, '${n.link || ''}')" data-notif-id="${n.id}">
            <div class="notif-item-icon ${n.type}"><i class="fas ${icon}"></i></div>
            <div class="notif-item-body">
                <div class="notif-item-title">${n.title}</div>
                <div class="notif-item-msg">${n.message}</div>
                <div class="notif-item-time">${timeAgo}</div>
            </div>
        </div>
    `;
}

function getTimeAgo(dateStr) {
    if (!dateStr) return '';
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return formatDate(dateStr);
}

async function fetchUnreadCount() {
    try {
        const data = await api.get('/notifications/unread-count');
        if (data === null) return;
        const badge = document.getElementById('notifBadge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (err) {
        console.error('Failed to fetch unread count:', err);
    }
}

async function fetchRecentNotifications() {
    try {
        const notifs = await api.get('/notifications?limit=10');
        if (notifs === null) return;
        const list = document.getElementById('notifList');
        if (!list) return;
        if (notifs.length === 0) {
            list.innerHTML = '<div class="notif-empty">No notifications yet</div>';
        } else {
            list.innerHTML = notifs.map(renderNotifItem).join('');
        }
    } catch (err) {
        console.error('Failed to fetch notifications:', err);
    }
}

async function handleNotifClick(notifId, link) {
    try {
        await api.put(`/notifications/${notifId}/read`);
        const item = document.querySelector(`[data-notif-id="${notifId}"]`);
        if (item) item.classList.remove('unread');
        fetchUnreadCount();
        if (link) {
            window.location.href = link;
        }
    } catch (err) {
        console.error('Failed to mark notification read:', err);
    }
}

async function markAllNotifRead(e) {
    if (e) e.stopPropagation();
    try {
        await api.put('/notifications/read-all');
        document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
        fetchUnreadCount();
    } catch (err) {
        console.error('Failed to mark all read:', err);
    }
}

function startNotifPolling() {
    stopNotifPolling();
    fetchUnreadCount();
    fetchRecentNotifications();
    _notifPollInterval = setInterval(fetchUnreadCount, 30000);
    _notifRecentInterval = setInterval(fetchRecentNotifications, 30000);
}

function stopNotifPolling() {
    if (_notifPollInterval) clearInterval(_notifPollInterval);
    if (_notifRecentInterval) clearInterval(_notifRecentInterval);
    _notifPollInterval = null;
    _notifRecentInterval = null;
}

window.addEventListener('beforeunload', stopNotifPolling);

// ===== MESSAGE UNREAD COUNT =====

let _msgPollInterval = null;

async function fetchMsgUnreadCount() {
    try {
        const data = await api.get('/messages/unread-count');
        if (data === null) return;
        const badge = document.getElementById('msgBadge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (err) {
        // silent
    }
}

function startMsgPolling() {
    if (_msgPollInterval) clearInterval(_msgPollInterval);
    fetchMsgUnreadCount();
    _msgPollInterval = setInterval(fetchMsgUnreadCount, 30000);
}
