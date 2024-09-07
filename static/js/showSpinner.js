document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("showSpinner");
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    const payNowBtn = document.getElementById('payNowBtn');

    form.addEventListener("submit", function(e) {
        payNowBtn.disabled = true;
        loadingModal.show();
    });
});
