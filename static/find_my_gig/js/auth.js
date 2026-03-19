document.addEventListener('DOMContentLoaded', function () {
    const signUpForm = document.getElementById('sign-up-form');

    //Sign up Form
    if (signUpForm) {

        //Band / Musician Radio Button
        const bandRadio = document.getElementById('radio-band');
        const musicianRadio = document.getElementById('radio-musician');

        if (bandRadio && musicianRadio) {
            [bandRadio, musicianRadio].forEach(function (radio) {
                radio.addEventListener('change', function () {
                    bandRadio.parentElement.classList.remove('radio-selected');
                    musicianRadio.parentElement.classList.remove('radio-selected');
                    this.parentElement.classList.add('radio-selected');
                });
            });
        }

        //Sign Up Form Submission Validation
        signUpForm.addEventListener('submit', function (e) {

            clearErrors();

            // Grab the values from each field
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            let hasError = false;

            // Username check 
            if (username === '') {
                showFieldError('username-error', 'Please enter a username');
                hasError = true;
            }

            //Email check
            if (email === '') {
                showFieldError('email-error', 'Please enter your email address');
                hasError = true;
            } else if (!isValidEmail(email)) {
                showFieldError('email-error', 'Please enter a valid email address');
                hasError = true;
            }

            //Account type check
            if (bandRadio && musicianRadio) {
                if (!bandRadio.checked && !musicianRadio.checked) {
                    showFieldError('account-type-error', 'Please select Band or Musician');
                    hasError = true;
                }
            }

            //Password check
            if (password === '') {
                showFieldError('password-error', 'Please enter a password');
                hasError = true;
            } else if (password.length < 8) {
                showFieldError('password-error', 'Password must be at least 8 characters');
                hasError = true;
            }

            //Confirm password check
            if (confirmPassword === '') {
                showFieldError('confirm-password-error', 'Please confirm your password');
                hasError = true;
            } else if (password !== confirmPassword) {
                showFieldError('confirm-password-error', 'Passwords do not match');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
            }

        });
    }

    //Login
    const loginForm = document.getElementById('login-form');

    if (loginForm) {

        //Show/Hide Password on Login
        const toggleLoginPassword = document.getElementById('toggle-login-password');
        const loginPasswordField = document.getElementById('login-password');

        if (toggleLoginPassword && loginPasswordField) {
            toggleLoginPassword.addEventListener('click', function () {
                if (loginPasswordField.type === 'password') {
                    loginPasswordField.type = 'text';
                    toggleLoginPassword.textContent = 'Hide';
                } else {
                    loginPasswordField.type = 'password';
                    toggleLoginPassword.textContent = 'Show';
                }
            });
        }

        //Login Form Submission Validation
        loginForm.addEventListener('submit', function (e) {

            clearErrors();

            const username = document.getElementById('login-username').value.trim();
            const password = loginPasswordField.value;

            let hasError = false;

            //Username check
            if (username === '') {
                showFieldError('login-username-error', 'Please enter your username');
                hasError = true;
            }

            //Password check
            if (password === '') {
                showFieldError('login-password-error', 'Please enter your password');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
            }

        });

        //Failed Login Error Message
        const loginError = document.getElementById('login-error-message');
        if (loginError) {
            // Shake the form gently to draw attention to the error
            loginForm.classList.add('form-shake');
            // Remove the shake class after animation finishes
            setTimeout(function () {
                loginForm.classList.remove('form-shake');
            }, 500);
        }

    }

    
    // Password reset page
    const passwordResetForm = document.getElementById('password-reset-form');

    if (passwordResetForm) {

        passwordResetForm.addEventListener('submit', function (e) {

            clearErrors();

            const email = document.getElementById('reset-email').value.trim();

            let hasError = false;

            // Email check
            if (email === '') {
                showFieldError('reset-email-error', 'Please enter your email address');
                hasError = true;
            } else if (!isValidEmail(email)) {
                showFieldError('reset-email-error', 'Please enter a valid email address');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
            }

        });
    }

});

//Helper Functions

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.classList.add('field-error');
    }
}

function clearErrors() {
    const allErrors = document.querySelectorAll('.field-error');
    allErrors.forEach(function (error) {
        error.textContent = '';
        error.style.display = 'none';
        error.classList.remove('field-error');
    });
}