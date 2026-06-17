class Auth {
    static getUser() {
        const user = localStorage.getItem('jnhs_user');
        return user ? JSON.parse(user) : null;
    }

    static setUser(user) {
        localStorage.setItem('jnhs_user', JSON.stringify(user));
    }

    static isLoggedIn() {
        return !!localStorage.getItem('jnhs_token');
    }

    static getRole() {
        const user = this.getUser();
        return user ? user.role : null;
    }

    static logout() {
        api.clearToken();
        window.location.href = '/login.html';
    }

    static requireAuth(allowedRoles = []) {
        if (!this.isLoggedIn()) {
            window.location.href = '/login.html';
            return false;
        }
        if (allowedRoles.length > 0 && !allowedRoles.includes(this.getRole())) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }
}
