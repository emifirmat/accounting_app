document.addEventListener('DOMContentLoaded', () => {
    const deleteButton = document.querySelector('#delete-button');
    const invoiceId = deleteButton.dataset.id;
    const invoiceType = deleteButton.dataset.type;
    const pos = deleteButton.dataset.pos;
    const invoiceNumber = deleteButton.dataset.number;
    const invoice = {id: invoiceId, type: invoiceType, point_of_sell: pos,
        number: invoiceNumber};

    // Call function from delte_invoice.js and redirect
    deleteButton.addEventListener('click', async () => {
        await deleteInvoice(invoice);
        setTimeout(() => window.location.href = "/erp/sales", 500);
    });
        
})