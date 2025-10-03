document.addEventListener('DOMContentLoaded', function () {
    // Initialize tooltips with mobile-friendly options
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        // Enable tooltips to work on mobile with touch events
        new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus click', // Added click for mobile devices
            placement: 'auto', // Auto adjust placement on small screens
            html: true, // Allow HTML content in tooltips
            animation: true, // Enable smooth animations
            delay: { show: 300, hide: 100 }, // Add delays for better UX
            customClass: 'custom-tooltip', // Add custom class for styling
            boundary: 'window' // Keep tooltip within window bounds
        });
    });

    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            var input = this.previousElementSibling; // target the input inside position-relative
            var icon = this.querySelector('i');
            if (input.type === "password") {
                input.type = "text";
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = "password";
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    });

    // Password strength indicator
    function checkStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[A-Z]/)) strength++;
        if (password.match(/[a-z]/)) strength++;
        if (password.match(/[0-9]/)) strength++;
        if (password.match(/[\W]/)) strength++;
        return strength;
    }

    document.querySelectorAll('input[type="password"], input[type="text"]').forEach(function(input) {
        input.addEventListener('input', function() {
            var strengthEl = document.getElementById(input.id + '-strength');
            if (!strengthEl) return;
            var strength = checkStrength(input.value);
            var text = "";
            var color = "";
            if (strength <= 2) {
                text = "Weak";
                color = "text-danger";
            } else if (strength === 3 || strength === 4) {
                text = "Medium";
                color = "text-warning";
            } else {
                text = "Strong";
                color = "text-success";
            }
            strengthEl.textContent = text;
            strengthEl.className = "form-text mt-1 " + color;
        });
    });
});