/**
 * Retrieves the value of a specific cookie (used primarily for CSRF tokens).
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        cookies.forEach(function (cookie) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
            }
        });
    }
    return cookieValue;
}

/**
 * Displays a temporary status message on the screen.
 */
function showStatusMessage(elementId, message, type) {
    const messageDiv = document.getElementById(elementId);
    if (messageDiv) {
        messageDiv.textContent = message;
        messageDiv.className = 'status-' + type;
        messageDiv.style.display = 'block';

        setTimeout(function () {
            messageDiv.style.display = 'none';
            messageDiv.textContent = '';
        }, 3000);
    }
}

/**
 * Checks if the body tag indicates an authenticated session.
 */
function isLoggedIn() {
    return document.body.classList.contains('user-logged-in');
}

/**
 * Redirects unauthenticated users to the login page, retaining their current destination.
 */
function redirectToLogin() {
    const currentPage = window.location.pathname;
    window.location.href = '/login/?next=' + currentPage;
}

/**
 * Formats a date string into a standard GB format (e.g., 25 December 2024).
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { day: 'numeric', month: 'long', year: 'numeric' };
    return date.toLocaleDateString('en-GB', options);
}

// ==========================================================================
// FORCE FRESH DATA ON BACK NAVIGATION (Bust the bfcache)
// ==========================================================================
window.addEventListener('pageshow', function (event) {
    // 'event.persisted' is true if the page was loaded from the browser's cache
    if (event.persisted) {
        // Force the browser to silently reload the page and ask Django for fresh data
        window.location.reload();
    }
});