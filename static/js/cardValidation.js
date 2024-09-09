document.addEventListener('DOMContentLoaded', function () {
    // Card number formatting
    const cardNumberInput = document.getElementById('card_number');
    cardNumberInput.addEventListener('input', function (e) {
        let cardNumber = e.target.value.replace(/\D/g, ''); // Remove non-digit characters
        let formattedCardNumber = cardNumber.replace(/(.{4})/g, '$1 ').trim(); // Insert a space every 4 digits

        // Set the value back to the input with the formatting
        e.target.value = formattedCardNumber;
    });

    // Expiry date formatting (MM/YY)
    const expiryDateInput = document.getElementById('expiry_date');
    expiryDateInput.addEventListener('input', function (e) {
        let input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters
        if (input.length > 2) {
            input = input.slice(0, 2) + '/' + input.slice(2); // Insert a slash after the month part
        }
        e.target.value = input;
    });

    // CVV Number Validation (3 or 4 digits)
    const cvcNumberInput = document.getElementById('cvc_number');
    cvcNumberInput.addEventListener('input', function (e) {
        let cvcNumber = e.target.value.replace(/\D/g, ''); // Only allow digits
        if (cvcNumber.length > 4) {
            cvcNumber = cvcNumber.slice(0, 4); // Limit to 4 digits max
        }
        e.target.value = cvcNumber;
    });
});
