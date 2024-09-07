document.addEventListener('DOMContentLoaded', function () {
    const ticketTable = document.getElementById('ticketTable');
    const grandTotalElem = document.getElementById('grandTotal');
    const amountInput = document.getElementById('amountInput');
    const ticketQuantity = document.getElementById('ticketQuantity');

    function updateGrandTotal() {
        let grandTotal = 0;
        // Loop through selected categories to calculate the grand total
        document.querySelectorAll('.category-radio:checked').forEach(function (radio) {
            const row = radio.closest('tr');
            const totalElem = row.querySelector('.category-total');
            grandTotal += parseFloat(totalElem.textContent);
        });
        amountInput.value = grandTotal;
        // Update the grand total display without decimals
        grandTotalElem.textContent = Math.round(grandTotal);
    }

    ticketTable.addEventListener('change', function (e) {
        if (e.target.classList.contains('category-radio')) {
            const row = e.target.closest('tr');
            const addButton = row.querySelector('.add-ticket');
            const removeButton = row.querySelector('.remove-ticket');
            const quantityElem = row.querySelector('.quantity');
            const totalElem = row.querySelector('.category-total');
            const price = parseFloat(row.dataset.price);

            // Deselect all other radios
            document.querySelectorAll('.category-radio').forEach(function (radio) {
                if (radio !== e.target) {
                    const otherRow = radio.closest('tr');
                    const otherAddButton = otherRow.querySelector('.add-ticket');
                    const otherRemoveButton = otherRow.querySelector('.remove-ticket');
                    const otherQuantityElem = otherRow.querySelector('.quantity');
                    const otherTotalElem = otherRow.querySelector('.category-total');

                    otherQuantityElem.textContent = 0;
                    otherTotalElem.textContent = 0;
                    otherAddButton.disabled = true;
                    otherRemoveButton.disabled = true;
                }
            });

            if (e.target.checked) {
                // Set quantity to 1 and enable buttons for the selected category
                quantityElem.textContent = 1;
                totalElem.textContent = Math.round(1 * price);
                addButton.disabled = false;
                removeButton.disabled = false;
            } else {
                // Reset quantity and disable buttons if the radio is deselected
                quantityElem.textContent = 0;
                totalElem.textContent = 0;
                addButton.disabled = true;
                removeButton.disabled = true;
            }
            updateGrandTotal();
        }
    });

    ticketTable.addEventListener('click', function (e) {
        if (e.target.classList.contains('add-ticket') || e.target.classList.contains('remove-ticket')) {
            const row = e.target.closest('tr');
            const radio = row.querySelector('.category-radio');
            const quantityElem = row.querySelector('.quantity');
            const totalElem = row.querySelector('.category-total');
            const price = parseFloat(row.dataset.price);
            let quantity = parseInt(quantityElem.textContent, 10);

            if (e.target.classList.contains('add-ticket')) {
                quantity++;
                radio.checked = true; // Automatically select category
            } else if (e.target.classList.contains('remove-ticket') && quantity > 0) {
                quantity--;
            }

            // Update quantity and total for the row
            quantityElem.textContent = quantity;
            ticketQuantity.value = quantity;
            totalElem.textContent = Math.round(quantity * price);

            // Handle category deselection and button disabling if quantity reaches 0
            if (quantity === 0) {
                radio.checked = false;
                row.querySelector('.add-ticket').disabled = true;
                row.querySelector('.remove-ticket').disabled = true;
            } else {
                row.querySelector('.add-ticket').disabled = false;
                row.querySelector('.remove-ticket').disabled = false;
            }

            updateGrandTotal(); // Recalculate grand total
        }
    });
});
