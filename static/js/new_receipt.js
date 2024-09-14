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

    try {
        return fetch('/erp/api/sale_invoices/' + relatedInvoice) 
        .then(response => {
            if (!response.ok) {
                throw new Error("Couldn't get related invoice");
            } else {
                return response.json();
            }
        })
        .then(result => {
            return result.recipient;
        })
    } catch (error) {
        console.error('Error' + error);
    }

}

