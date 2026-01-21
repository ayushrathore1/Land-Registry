/**
 * Authentication Manager - Handles user authentication and session
 */

const AuthManager = {
    currentUser: null,
    onAuthChange: null,

    /**
     * Initialize auth manager
     */
    init() {
        // Check for existing session
        const userData = localStorage.getItem('user_data');
        if (userData) {
            this.currentUser = JSON.parse(userData);
            this.updateUI();
            this.verifySession();
        }

        this.bindEvents();
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        // Login button
        document.getElementById('loginBtn')?.addEventListener('click', () => {
            this.showLoginModal();
        });

        // Close login modal
        document.getElementById('closeLoginBtn')?.addEventListener('click', () => {
            this.hideLoginModal();
        });

        // Login form submit
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Close modal on backdrop click
        document.getElementById('loginModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'loginModal') {
                this.hideLoginModal();
            }
        });
    },

    /**
     * Verify current session
     */
    async verifySession() {
        try {
            await API.verifyToken();
        } catch (error) {
            // Token invalid, clear session
            this.logout();
        }
    },

    /**
     * Show login modal
     */
    showLoginModal() {
        document.getElementById('loginModal').classList.add('active');
        document.getElementById('username').focus();
    },

    /**
     * Hide login modal
     */
    hideLoginModal() {
        document.getElementById('loginModal').classList.remove('active');
        document.getElementById('loginForm').reset();
        document.getElementById('loginError').classList.remove('active');
    },

    /**
     * Handle login form submission
     */
    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorEl = document.getElementById('loginError');

        try {
            const response = await API.login(username, password);
            this.currentUser = response.user;
            this.hideLoginModal();
            this.updateUI();
            
            App.showToast('Logged in successfully', 'success');

            if (this.onAuthChange) {
                this.onAuthChange(this.currentUser);
            }
        } catch (error) {
            errorEl.textContent = error.message;
            errorEl.classList.add('active');
        }
    },

    /**
     * Logout user
     */
    logout() {
        API.logout();
        this.currentUser = null;
        this.updateUI();

        if (this.onAuthChange) {
            this.onAuthChange(null);
        }

        App.showToast('Logged out', 'success');
    },

    /**
     * Update UI based on auth state
     */
    updateUI() {
        const userSection = document.getElementById('userSection');

        if (this.currentUser) {
            const initials = this.currentUser.full_name
                .split(' ')
                .map(n => n[0])
                .join('')
                .toUpperCase();

            userSection.innerHTML = `
                <div class="user-info">
                    <div class="user-avatar">${initials}</div>
                    <div>
                        <div class="user-name">${this.currentUser.full_name}</div>
                        <div class="user-role">${this.currentUser.role}</div>
                    </div>
                </div>
                <button class="btn btn-outline btn-sm" id="logoutBtn">Logout</button>
            `;

            document.getElementById('logoutBtn').addEventListener('click', () => {
                this.logout();
            });
        } else {
            userSection.innerHTML = `
                <button class="btn btn-outline" id="loginBtn">Login</button>
            `;

            document.getElementById('loginBtn').addEventListener('click', () => {
                this.showLoginModal();
            });
        }
    },

    /**
     * Check if user has required role
     */
    hasRole(requiredRole) {
        if (!this.currentUser) return false;

        const roleHierarchy = { viewer: 1, editor: 2, admin: 3 };
        const userLevel = roleHierarchy[this.currentUser.role] || 0;
        const requiredLevel = roleHierarchy[requiredRole] || 0;

        return userLevel >= requiredLevel;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.currentUser;
    }
};

window.AuthManager = AuthManager;
