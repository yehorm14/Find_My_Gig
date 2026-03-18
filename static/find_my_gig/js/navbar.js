document.addEventListener('DOMContentLoaded', function () {

    const hamburgerBtn = document.getElementById('hamburger-btn');
    const navMenu = document.getElementById('nav-menu');

    //Hamburger menu for smaller screens
    if (hamburgerBtn && navMenu) {
        hamburgerBtn.addEventListener('click', function () {
            navMenu.classList.toggle('nav-open');
        });

        document.addEventListener('click', function (e) {
            if (!hamburgerBtn.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('nav-open');
            }
        });
    }

    //Active nav link 
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(function (link) {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath || currentPath.startsWith(linkPath) && linkPath !== '/') {
            link.classList.add('nav-active');
        }
    });

    //Sign out button
    const signOutBtn = document.getElementById('sign-out-btn');

    if (signOutBtn) {
        signOutBtn.addEventListener('click', function (e) {
            e.preventDefault();

            const confirmed = confirm('Are you sure you want to sign out?');
            if (confirmed) {
                const logoutForm = document.getElementById('logout-form');
                if (logoutForm) {
                    logoutForm.submit();
                } else {
                    window.location.href = this.getAttribute('href');
                }
            }
        });
    }
});