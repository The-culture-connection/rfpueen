// RFP Queen - Standalone Web Application
(function() {
    'use strict';

    // Firebase Configuration
    const firebaseConfig = {
        apiKey: "AIzaSyDbkrUWV13zBvl4L2lu5Qw5aLYbC9LCjJk",
        authDomain: "therfpqueen.firebaseapp.com",
        projectId: "therfpqueen-f11fd"
    };

    // Initialize Firebase
    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
    }
    const auth = firebase.auth();
    const db = firebase.firestore();

    // Collection mapping
    const COLLECTION_MAP = {
        "Contracts": ["SAM"],
        "Grants": ["grants.gov", "grantwatch"],
        "RFPs": ["PND_RFPs", "rfpmart"],
        "Bids": ["bid"]
    };

    // App state
    const state = {
        currentUser: null,
        currentPage: 'dashboard',
        items: [],
        shown: 0,
        pageSize: 20,
        profile: null,
        loading: false
    };

    // Initialize app
    function init() {
        const root = document.getElementById('app-root');
        if (!root) {
            console.error('App root not found');
            return;
        }

        // Listen for auth state changes
        auth.onAuthStateChanged(async (user) => {
            state.currentUser = user;
            if (user) {
                state.email = user.email;
                renderPage();
            } else {
                renderLogin();
            }
        });

        // Handle routing
        window.addEventListener('hashchange', () => {
            renderPage();
        });

        // Initial render
        if (window.location.hash) {
            renderPage();
        } else {
            window.location.hash = '#dashboard';
        }
    }

    // Routing
    function getCurrentPage() {
        const hash = window.location.hash.replace('#', '') || 'dashboard';
        return hash;
    }

    // Render based on route
    function renderPage() {
        const page = getCurrentPage();
        state.currentPage = page;
        
        switch(page) {
            case 'login':
                renderLogin();
                break;
            case 'explore':
                renderExplore();
                break;
            case 'dashboard':
                renderDashboard();
                break;
            case 'applied':
                renderApplied();
                break;
            case 'saved':
                renderSaved();
                break;
            default:
                renderDashboard();
        }
    }

    // Navigation component
    function renderNav() {
        return `
            <nav class="nav">
                <div class="nav-content">
                    <div>
                        <strong>RFP Queen</strong> • ${state.currentUser ? `Signed in as ${state.currentUser.email}` : 'Not signed in'}
                    </div>
                    <div class="nav-links">
                        ${state.currentUser ? `
                            <a href="#dashboard" class="btn btn-secondary">Dashboard</a>
                            <a href="#explore" class="btn btn-primary">Explore</a>
                            <a href="#applied" class="btn btn-secondary">Applied</a>
                            <a href="#saved" class="btn btn-secondary">Saved</a>
                            <button onclick="app.signOut()" class="btn btn-outline">Sign Out</button>
                        ` : `
                            <a href="#login" class="btn btn-primary">Sign In</a>
                        `}
                    </div>
                </div>
            </nav>
        `;
    }

    // Alert system
    function showAlert(message, type = 'info', title = null) {
        const alertId = 'alert-' + Date.now();
        const icons = {
            error: '⚠️',
            success: '✅',
            info: 'ℹ️',
            warning: '⚠️'
        };
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type}">
                <div class="alert-icon">${icons[type] || icons.info}</div>
                <div class="alert-content">
                    ${title ? `<span class="alert-title">${title}</span>` : ''}
                    <div class="alert-message">${message}</div>
                    <button class="alert-dismiss" onclick="document.getElementById('${alertId}').remove()">Dismiss</button>
                </div>
            </div>
        `;
        
        const root = document.getElementById('app-root');
        const existing = root.querySelector('.alert');
        if (existing) existing.remove();
        
        root.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                const alert = document.getElementById(alertId);
                if (alert) alert.remove();
            }, 5000);
        }
    }

    // Login page
    function renderLogin() {
        const root = document.getElementById('app-root');
        root.innerHTML = `
            ${renderNav()}
            <div class="login-container">
                <h2 class="login-title">Sign In</h2>
                <p class="login-subtitle">Enter your email and password to access your dashboard.</p>
                <div id="login-error" class="form-error"></div>
                <form id="login-form" onsubmit="return app.handleLogin(event)">
                    <div class="form-group">
                        <label class="form-label" for="login-email">Email</label>
                        <input class="form-input" id="login-email" type="email" placeholder="Email" required autocomplete="email">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="login-password">Password</label>
                        <input class="form-input" id="login-password" type="password" placeholder="Password" required autocomplete="current-password">
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%">Log In</button>
                </form>
            </div>
        `;
    }

    // Dashboard page
    async function renderDashboard() {
        if (!state.currentUser) {
            window.location.hash = '#login';
            return;
        }

        const root = document.getElementById('app-root');
        root.innerHTML = `
            ${renderNav()}
            <div class="container">
                <h1>Dashboard</h1>
                <div class="dashboard-grid">
                    <a href="#explore" class="dashboard-card">
                        <div class="dashboard-card-icon">🔍</div>
                        <h3 class="dashboard-card-title">Explore Opportunities</h3>
                        <p class="dashboard-card-text">Find new opportunities matched to your profile</p>
                    </a>
                    <a href="#applied" class="dashboard-card">
                        <div class="dashboard-card-icon">📝</div>
                        <h3 class="dashboard-card-title">Applied Opportunities</h3>
                        <p class="dashboard-card-text">View opportunities you've applied to</p>
                    </a>
                    <a href="#saved" class="dashboard-card">
                        <div class="dashboard-card-icon">💾</div>
                        <h3 class="dashboard-card-title">Saved Opportunities</h3>
                        <p class="dashboard-card-text">View opportunities saved for later</p>
                    </a>
                </div>
            </div>
        `;
    }

    // Explore page - Simplified version that loads from explore.html logic
    function renderExplore() {
        if (!state.currentUser) {
            window.location.hash = '#login';
            return;
        }

        const root = document.getElementById('app-root');
        root.innerHTML = `
            ${renderNav()}
            <div class="container">
                <h1>Explore Opportunities</h1>
                <div style="margin: 20px 0;">
                    <button id="find-matches-btn" class="btn btn-primary" onclick="app.findMatches()">Find Matches</button>
                </div>
                <div id="explore-content">
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Click "Find Matches" to discover opportunities</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Applied page
    async function renderApplied() {
        if (!state.currentUser) {
            window.location.hash = '#login';
            return;
        }

        const root = document.getElementById('app-root');
        root.innerHTML = `
            ${renderNav()}
            <div class="container">
                <h1>Applied Opportunities</h1>
                <div id="applied-content" class="loading">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            </div>
        `;

        await loadApplied();
    }

    // Saved page
    async function renderSaved() {
        if (!state.currentUser) {
            window.location.hash = '#login';
            return;
        }

        const root = document.getElementById('app-root');
        root.innerHTML = `
            ${renderNav()}
            <div class="container">
                <h1>Saved Opportunities</h1>
                <div id="saved-content" class="loading">
                    <div class="spinner"></div>
                    <p>Loading...</p>
                </div>
            </div>
        `;

        await loadSaved();
    }

    // Load applied opportunities
    async function loadApplied() {
        try {
            const snap = await db.collection("profiles").doc(state.currentUser.uid)
                .collection("Applied").orderBy("appliedAt", "desc").limit(100).get();
            
            const items = snap.docs.map(d => ({ id: d.id, ...d.data() }));
            renderOpportunityList('applied-content', items, 'applied');
        } catch (e) {
            showAlert(`Failed to load applied opportunities: ${e.message}`, 'error');
            document.getElementById('applied-content').innerHTML = '<p>Error loading opportunities</p>';
        }
    }

    // Load saved opportunities
    async function loadSaved() {
        try {
            const snap = await db.collection("profiles").doc(state.currentUser.uid)
                .collection("Saved").orderBy("savedAt", "desc").limit(100).get();
            
            const items = snap.docs.map(d => ({ id: d.id, ...d.data() }));
            renderOpportunityList('saved-content', items, 'saved');
        } catch (e) {
            showAlert(`Failed to load saved opportunities: ${e.message}`, 'error');
            document.getElementById('saved-content').innerHTML = '<p>Error loading opportunities</p>';
        }
    }

    // Render opportunity list
    function renderOpportunityList(containerId, items, type) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (items.length === 0) {
            container.innerHTML = `<p class="text-center">No ${type} opportunities yet.</p>`;
            return;
        }

        container.innerHTML = items.map((item, index) => renderOpportunityCard(item, index, type)).join('');
    }

    // Render opportunity card
    function renderOpportunityCard(opp, index, type) {
        const urgency = getUrgency(opp.closeDate || opp.deadline);
        const urgencyClass = `badge-${urgency}`;
        
        return `
            <div class="card">
                <div class="card-header">
                    <span class="badge badge-source">${opp.collection || type}</span>
                    <span class="badge ${urgencyClass}">${urgency}</span>
                    ${type === 'applied' ? '<span class="badge badge-success">Applied</span>' : ''}
                    ${type === 'saved' ? '<span class="badge badge-info">Saved</span>' : ''}
                </div>
                <h3 class="card-title">${opp.title || 'Untitled Opportunity'}</h3>
                <p class="card-subtitle">${opp.agency || opp.department || 'Unknown Agency'}</p>
                <div class="card-description">${(opp.description || opp.summary || '').substring(0, 200)}...</div>
                <div class="card-meta">
                    <div><strong>Deadline:</strong> ${opp.closeDate ? new Date(opp.closeDate).toLocaleDateString() : '—'}</div>
                    <div><strong>Location:</strong> ${opp.place || [opp.city, opp.state].filter(Boolean).join(', ') || '—'}</div>
                </div>
                <div class="card-actions">
                    ${opp.applicationUrl ? `
                        <a href="${opp.applicationUrl}" target="_blank" class="btn btn-primary">Open Application</a>
                    ` : ''}
                    <a href="${opp.url || '#'}" target="_blank" class="btn btn-secondary">View Details</a>
                    <button onclick="app.removeOpportunity('${opp.id}', '${type}', ${index})" class="btn btn-danger">Remove</button>
                </div>
            </div>
        `;
    }

    // Get urgency badge
    function getUrgency(deadline) {
        if (!deadline) return 'ongoing';
        const days = Math.ceil((new Date(deadline) - new Date()) / 86400000);
        if (days <= 30) return 'urgent';
        if (days <= 92) return 'soon';
        return 'ongoing';
    }

    // Public API
    window.app = {
        handleLogin: async function(e) {
            e.preventDefault();
            const errorEl = document.getElementById('login-error');
            const email = document.getElementById('login-email').value.trim();
            const password = document.getElementById('login-password').value;

            errorEl.classList.remove('show');
            errorEl.textContent = '';

            try {
                await auth.signInWithEmailAndPassword(email, password);
                window.location.hash = '#dashboard';
            } catch (e) {
                let errorMsg = 'Login failed';
                if (e.code === 'auth/user-not-found') {
                    errorMsg = 'No account found with this email address.';
                } else if (e.code === 'auth/wrong-password') {
                    errorMsg = 'Incorrect password.';
                } else if (e.code === 'auth/invalid-email') {
                    errorMsg = 'Invalid email address format.';
                } else {
                    errorMsg = e.message.replace('Firebase: ', '');
                }
                errorEl.textContent = errorMsg;
                errorEl.classList.add('show');
            }
        },

        signOut: async function() {
            try {
                await auth.signOut();
                window.location.hash = '#login';
            } catch (e) {
                showAlert(`Failed to sign out: ${e.message}`, 'error');
            }
        },

        findMatches: async function() {
            showAlert('Matching functionality requires full implementation. Please use the explore.html file for full functionality.', 'info');
        },

        removeOpportunity: async function(oppId, type, index) {
            if (!confirm(`Remove this opportunity from your ${type} list?`)) return;
            
            try {
                await db.collection("profiles").doc(state.currentUser.uid)
                    .collection(type === 'applied' ? 'Applied' : 'Saved').doc(oppId).delete();
                
                showAlert('Opportunity removed successfully.', 'success');
                if (type === 'applied') renderApplied();
                else renderSaved();
            } catch (e) {
                showAlert(`Failed to remove: ${e.message}`, 'error');
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
