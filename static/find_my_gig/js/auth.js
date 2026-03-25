document.addEventListener('DOMContentLoaded', function () {

    /* ==========================================================================
       1. SIGN UP FLOW
       ========================================================================== */
    const signUpForm = document.getElementById('sign-up-form');

    if (signUpForm) {
        const bandRadio = document.getElementById('radio-band');
        const musicianRadio = document.getElementById('radio-musician');

        // Toggle visual styling for the radio buttons
        if (bandRadio && musicianRadio) {
            [bandRadio, musicianRadio].forEach(function (radio) {
                radio.addEventListener('click', function () {
                    bandRadio.parentElement.classList.remove('radio-selected');
                    musicianRadio.parentElement.classList.remove('radio-selected');
                    this.parentElement.classList.add('radio-selected');
                });
            });
        }

        // Form Submission Validation
        signUpForm.addEventListener('submit', function (e) {
            clearErrors();
            let hasError = false;

            // Grab the values
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            // Validate Username
            if (username === '') {
                showFieldError('username-error', 'Please enter a username');
                hasError = true;
            }

            // Validate Email
            if (email === '') {
                showFieldError('email-error', 'Please enter your email address');
                hasError = true;
            } else if (!isValidEmail(email)) {
                showFieldError('email-error', 'Please enter a valid email address');
                hasError = true;
            }

            // Validate Account Type Selection
            if (bandRadio && musicianRadio) {
                if (!bandRadio.checked && !musicianRadio.checked) {
                    showFieldError('account-type-error', 'Please select Band or Musician');
                    hasError = true;
                }
            }

            // Validate Band Name if Band is selected
            if (bandRadio && bandRadio.checked) {
                const bandName = document.getElementById('band-name').value.trim();
                if (bandName === '') {
                    showFieldError('band-name-error', 'Please enter your band or venue name');
                    hasError = true;
                }
            }

            // Validate Password
            if (password === '') {
                showFieldError('password-error', 'Please enter a password');
                hasError = true;
            } else if (password.length < 8) {
                showFieldError('password-error', 'Password must be at least 8 characters');
                hasError = true;
            }

            // Validate Confirm Password
            if (confirmPassword === '') {
                showFieldError('confirm-password-error', 'Please confirm your password');
                hasError = true;
            } else if (password !== confirmPassword) {
                showFieldError('confirm-password-error', 'Passwords do not match');
                hasError = true;
            }

            // Stop submission if errors exist
            if (hasError) {
                e.preventDefault();
            }
        });
    }

    /* ==========================================================================
       2. LOGIN FLOW
       ========================================================================== */
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        const toggleLoginPassword = document.getElementById('toggle-login-password');
        const loginPasswordField = document.getElementById('login-password');

        // Show/Hide Password Feature
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

        // Login Validation
        loginForm.addEventListener('submit', function (e) {
            clearErrors();
            let hasError = false;

            const username = document.getElementById('login-username').value.trim();
            const password = loginPasswordField.value;

            if (username === '') {
                showFieldError('login-username-error', 'Please enter your username');
                hasError = true;
            }

            if (password === '') {
                showFieldError('login-password-error', 'Please enter your password');
                hasError = true;
            }

            if (hasError) {
                e.preventDefault();
            }
        });

        // Form Shake Animation on Backend Error
        const loginError = document.getElementById('login-error-message');
        if (loginError && loginError.style.display !== 'none') {
            loginForm.classList.add('form-shake');
            setTimeout(function () {
                loginForm.classList.remove('form-shake');
            }, 500);
        }
    }

    /* ==========================================================================
       3. PASSWORD RESET FLOW & DJANGO FORM STYLING
       ========================================================================== */
    
    // Auto-styler: Injects our custom 'form-control' CSS class into Django's auto-generated inputs
    const djangoResetInputs = document.querySelectorAll('#reset-form input:not([type="hidden"]), #new-password-form input:not([type="hidden"])');
    if (djangoResetInputs.length > 0) {
        djangoResetInputs.forEach(input => {
            input.classList.add('form-control');
        });
    }

    // Reset Form Client-Side Validation
    const passwordResetForm = document.getElementById('reset-form');
    if (passwordResetForm) {
        passwordResetForm.addEventListener('submit', function (e) {
            clearErrors();
            let hasError = false;

            // Django generates the email input with the id 'id_email'
            const emailInput = document.getElementById('id_email');
            
            if (emailInput) {
                const email = emailInput.value.trim();
                
                if (email === '') {
                    // Creating a dynamic error span since Django doesn't generate one natively
                    let errorSpan = document.getElementById('reset-email-error');
                    if (!errorSpan) {
                        errorSpan = document.createElement('span');
                        errorSpan.id = 'reset-email-error';
                        errorSpan.className = 'text-danger small mt-1 field-error d-block';
                        emailInput.parentNode.appendChild(errorSpan);
                    }
                    errorSpan.textContent = 'Please enter your email address';
                    errorSpan.style.display = 'block';
                    hasError = true;
                } else if (!isValidEmail(email)) {
                    let errorSpan = document.getElementById('reset-email-error');
                    if (!errorSpan) {
                        errorSpan = document.createElement('span');
                        errorSpan.id = 'reset-email-error';
                        errorSpan.className = 'text-danger small mt-1 field-error d-block';
                        emailInput.parentNode.appendChild(errorSpan);
                    }
                    errorSpan.textContent = 'Please enter a valid email address';
                    errorSpan.style.display = 'block';
                    hasError = true;
                }
            }

            if (hasError) {
                e.preventDefault();
            }
        });
    }

});

/* ==========================================================================
   4. HELPER FUNCTIONS
   ========================================================================== */

function isValidEmail(email) {
    // Standard Regex for email validation
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