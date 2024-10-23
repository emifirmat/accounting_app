document.addEventListener('DOMContentLoaded', () => {
    // Get info from the commercial document and pass it to delete function

    const deleteButton = document.querySelector('#delete-button');
    const comDocument = deleteButton.dataset.document;
    const comDocumentId = deleteButton.dataset.id;
    const comDocumentPOS = deleteButton.dataset.pos;
    const comDocumentNumber = deleteButton.dataset.number;
    
    const comDocObject = {id: comDocumentId, point_of_sell: comDocumentPOS,
        number: comDocumentNumber};
    
    let invoiceType = '';
    let redirectUrl = '';

    if (comDocument === "invoice") {
        invoiceType = deleteButton.dataset.type;
        comDocObject.type = invoiceType;
        redirectUrl = '/erp/sales';
    } else if (comDocument === "receipt") {
        comDocObject.related_invoice = deleteButton.dataset.invoice;
        redirectUrl = '/erp/receivables';
    }

    // Call function from document_delete.js and redirect
    deleteButton.addEventListener('click', async () => 
        await deleteComDocument(comDocument, comDocObject, redirectUrl) // document_delete.js
    );
})