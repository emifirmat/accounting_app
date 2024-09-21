document.addEventListener('DOMContentLoaded', () => {

    // Autoselect client after related invoice
    const rInvoiceField = document.querySelector('#id_related_invoice');
    rInvoiceField.addEventListener('change', () => {
        if(rInvoiceField.value) {
            autoSelectClient(rInvoiceField.value);
        }
    });

})

async function autoSelectClient(relatedInvoice) {
    // get Client of related Invoice and pick the recipient
    
    const recipientField = document.querySelector("#id_recipient")
    const clientId = await getClientId(relatedInvoice)
    
    // Add it in recipient field 
    recipientField.value = clientId

}

async function getClientId(relatedInvoice) {
    // Go to invoice api and extract client id

    const invoice = await getList('/erp/api/sale_invoices/' + relatedInvoice);
            
    return invoice.recipient;
        
}


