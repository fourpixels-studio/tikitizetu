document.addEventListener('DOMContentLoaded', function() {
    // select the 3 containers
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');

    const firstName = document.querySelector('input[name="first_name"]');
    const lastName = document.querySelector('input[name="last_name"]');
    const email = document.querySelector('input[name="email"]');
    
    // Utility function to check if a field is empty
    function isFieldEmpty(field) {
        return field.value.trim() === '';
    }

    // Validate email format
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email.value.trim());
    }

    // Function to show an error message
    function showError(field, message) {
        field.classList.add('is-invalid');
        field.nextElementSibling.textContent = message;
    }

    // Function to hide the error message
    function hideError(field) {
        field.classList.remove('is-invalid');
        field.nextElementSibling.textContent = '';
    }

    // Function to create and show a toast notification
    function showToast(message) {
        const toastEl = document.getElementById('ticketCategoryToast');
        const toastBody = toastEl.querySelector('.toast-body');

        // Set the toast message
        toastBody.textContent = message;

        // Create a new toast instance and show it
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 10000 // Adjust time as needed (10000ms = 10 seconds)
        });
        toast.show();
    }


    // Validate step 1 fields
    function validateStep1() {
        let isValid = true;

        // First Name Validation
        if (isFieldEmpty(firstName)) {
            showToast('First name is required.');
            showError(firstName, 'First name is required.');
            isValid = false;
        } else {
            hideError(firstName);
        }

        // Last Name Validation
        if (isFieldEmpty(lastName)) {
            showToast('Last name is required.');
            showError(lastName, 'Last name is required.');
            isValid = false;
        } else {
            hideError(lastName);
        }

        // Email Validation
        if (isFieldEmpty(email)) {
            showToast('Please enter your email.');
            showError(email, 'Email is required.');
            isValid = false;
        } else if (!isValidEmail(email)) {
            showToast('Please enter a valid email.');
            showError(email, 'Please enter a valid email.');
            isValid = false;
        } else {
            hideError(email);
        }

        return isValid;
    }

    // Show step 2 only if validation passes
    function showStep2() {
        if (validateStep1()) {
            step2.classList.remove("hide");
            step2.classList.add("show");

            step1.classList.add("hide");
            step3.classList.add("hide");

            step1.classList.remove("show");
            step3.classList.remove("show");
        }
    }

    // Ensure at least one category is selected before showing step 3
    function validateStep2() {
        const selectedCategories = document.querySelectorAll('.category-radio:checked');
        if (selectedCategories.length === 0) {
            showToast("Please select at least one ticket category.");
            return false;
        }
        return true;
    }

    function showStep3() {
        if (validateStep2()) {
            step3.classList.remove("hide");
            step3.classList.add("show");

            step2.classList.add("hide");
            step1.classList.add("hide");

            step2.classList.remove("show");
            step1.classList.remove("show");
        }
    }

    // Hide ticket type container function
    function hideStep2() {
        if (step2.classList.contains("show")) {
            step2.classList.remove("show");
            step2.classList.add("hide");

            step3.classList.remove("show");
            step3.classList.add("hide");

            step1.classList.remove("hide");
            step1.classList.add("show");
        }
    }

        // Hide payment details container function
    function hideStep3() {
        if (step3.classList.contains("show")) {
            step3.classList.remove("show");
            step3.classList.add("hide");

            step2.classList.remove("hide");
            step2.classList.add("show");

            step1.classList.add("hide");
            step1.classList.remove("show");
        }
    }

    // Payment step validation
    function validatePaymentStep() {
        const termsCheckbox = document.querySelector('input[name="terms_conditions"]');

        if (!termsCheckbox.checked) {
            showToast("You must agree to the terms and conditions.");
            return false;
        }

        return true;
    }

    // selecting the show buttons
    const showStep2Btn = document.getElementById('showStep2Btn');
    const showStep3Btn = document.getElementById('showStep3Btn');

    // selecting the back buttons
    const backToStep1Btn = document.getElementById('backToStep1Btn');
    const backToStep2Btn = document.getElementById('backToStep2Btn');

    // event listeners to show containers
    showStep2Btn.addEventListener("click", showStep2);
    showStep3Btn.addEventListener("click", showStep3);

    // event listeners to hide containers
    backToStep1Btn.addEventListener("click", hideStep2);
    backToStep2Btn.addEventListener("click", hideStep3);

    // Attach payment validation to the "Pay Now" button
    const payNowButton = document.getElementById('payNowBtn');
    payNowButton.addEventListener('click', function(e) {
        if (!validatePaymentStep()) {
            e.preventDefault();
        }
    });
});
