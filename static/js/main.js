/**
 * ALAGA - Senior Citizen Health Intelligence Platform
 * Vanilla JavaScript Front-End Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
    initPasswordToggles();
    initRegistrationValidation();
    initFormSubmissionSpinners();
});

/**
 * 1. Password Visibility Toggle
 * Finds all buttons with `.password-toggle` and switches the targeted input
 * between 'password' and 'text'.
 */
function initPasswordToggles() {
    const toggles = document.querySelectorAll('.password-toggle');

    toggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = toggle.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);

            if (targetInput) {
                const isPassword = targetInput.getAttribute('type') === 'password';
                targetInput.setAttribute('type', isPassword ? 'text' : 'password');
                toggle.textContent = isPassword ? '🔒' : '👁';
                toggle.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
            }
        });
    });
}

/**
 * 2. Real-Time Password Matching & Validation
 * Listens to the `input` event on register password and confirm_password inputs.
 * Provides immediate visual feedback to reduce form submission errors.
 */
function initRegistrationValidation() {
    const registerForm = document.getElementById('registerForm');
    if (!registerForm) return;

    const pwdInput = document.getElementById('id_password');
    const confirmPwdInput = document.getElementById('id_confirm_password');
    const hint = document.getElementById('passwordMatchHint');

    if (!pwdInput || !confirmPwdInput || !hint) return;

    function checkPasswordsMatch() {
        const pwd = pwdInput.value;
        const confirm = confirmPwdInput.value;

        if (!confirm) {
            hint.textContent = '';
            hint.className = 'validation-hint';
            confirmPwdInput.classList.remove('is-invalid');
            return;
        }

        if (pwd === confirm) {
            hint.textContent = '✓ Passwords match';
            hint.className = 'validation-hint valid';
            confirmPwdInput.classList.remove('is-invalid');
        } else {
            hint.textContent = '✗ Passwords do not match';
            hint.className = 'validation-hint invalid';
            confirmPwdInput.classList.add('is-invalid');
        }
    }

    pwdInput.addEventListener('input', checkPasswordsMatch);
    confirmPwdInput.addEventListener('input', checkPasswordsMatch);
}

/**
 * 3. Double-Submit Prevention & Loading Indicator
 * Disables the submit button on submission and displays a loading spinner
 * to avoid duplicate POST actions on slower mobile networks.
 */
function initFormSubmissionSpinners() {
    const forms = document.querySelectorAll('form:not(.inline-form)');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitBtn = this.querySelector('.submit-btn');
            if (!submitBtn) return;

            // If HTML5 validation fails, abort spinner display
            if (!this.checkValidity()) {
                return;
            }

            const btnText = submitBtn.querySelector('.btn-text');
            const spinner = submitBtn.querySelector('.btn-spinner');

            if (spinner) {
                spinner.classList.remove('hide');
            }
            if (btnText) {
                btnText.textContent = 'Processing...';
            }

            // Temporarily disable button to prevent rapid double-clicks
            submitBtn.style.pointerEvents = 'none';
            submitBtn.setAttribute('disabled', 'true');
        });
    });
}