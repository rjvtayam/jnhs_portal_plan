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

function showNotification(message, type = 'success') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:inherit;cursor:pointer;font-size:1.2rem">&times;</button>
    `;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 9999;
        padding: 15px 20px; border-radius: 6px; display: flex; align-items: center; gap: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#f0fff4' : type === 'error' ? '#fff5f5' : '#ebf8ff'};
        color: ${type === 'success' ? '#276749' : type === 'error' ? '#9b2c2c' : '#2b6cb0'};
        border: 1px solid ${type === 'success' ? '#c6f6d5' : type === 'error' ? '#fed7d7' : '#bee3f8'};
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
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
        admin: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/admin/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Dashboard
                </a>
                <a href="/pages/admin/students.html" class="nav-item ${activePage === 'students' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Students
                </a>
                <a href="/pages/admin/teachers.html" class="nav-item ${activePage === 'teachers' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Teachers
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Academic</div>
                <a href="/pages/admin/enrollment.html" class="nav-item ${activePage === 'enrollment' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Enrollment
                </a>
                <a href="/pages/admin/grades.html" class="nav-item ${activePage === 'grades' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Grades
                </a>
                <a href="/pages/admin/reports.html" class="nav-item ${activePage === 'reports' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Reports
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Communication</div>
                <a href="/pages/admin/announcements.html" class="nav-item ${activePage === 'announcements' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Announcements
                </a>
            </div>
        `,
        teacher: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/teacher/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Dashboard
                </a>
                <a href="/pages/teacher/my-sections.html" class="nav-item ${activePage === 'sections' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> My Sections
                </a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Academic</div>
                <a href="/pages/teacher/grade-entry.html" class="nav-item ${activePage === 'grade-entry' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Grade Entry
                </a>
                <a href="/pages/teacher/attendance.html" class="nav-item ${activePage === 'attendance' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Attendance
                </a>
            </div>
        `,
        student: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/student/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Dashboard
                </a>
                <a href="/pages/student/grades.html" class="nav-item ${activePage === 'grades' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> My Grades
                </a>
                <a href="/pages/student/schedule.html" class="nav-item ${activePage === 'schedule' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Schedule
                </a>
                <a href="/pages/student/profile.html" class="nav-item ${activePage === 'profile' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Profile
                </a>
            </div>
        `,
        parent: `
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/pages/parent/dashboard.html" class="nav-item ${activePage === 'dashboard' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Dashboard
                </a>
                <a href="/pages/parent/child-progress.html" class="nav-item ${activePage === 'progress' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Child Progress
                </a>
                <a href="/pages/parent/announcements.html" class="nav-item ${activePage === 'announcements' ? 'active' : ''}">
                    <span class="icon">&#9632;</span> Announcements
                </a>
            </div>
        `,
    };

    return `
        <div class="sidebar-header">
            <div class="logo">J</div>
            <div class="school-name">Jomalig National High School</div>
        </div>
        <nav class="sidebar-nav">
            ${roleMenus[user.role] || ''}
        </nav>
        <div class="sidebar-footer">
            <div class="nav-item" onclick="Auth.logout()">
                <span class="icon">&#9632;</span> Logout
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
        userInfo.textContent = `${user.username} (${capitalize(user.role)})`;
    }
}
