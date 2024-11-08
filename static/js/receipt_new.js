document.addEventListener('DOMContentLoaded', () => {

    // Autoselect client after related invoice
    const rInvoiceField = document.querySelector('#id_related_invoice');
    rInvoiceField.addEventListener('change', () => {
        if(rInvoiceField.value) {
            autoSelectClient(rInvoiceField.value);
        }
    });

    // Create a checkbox to change related_receipts in form.
    const action = document.querySelector('#document-title').dataset.action
    let invoiceList;
    let checked = false;
    
    const check_box = createCheckbox(rInvoiceField.parentNode);
    check_box.addEventListener('change', async () => {
        // Only ask for the invoice list if it's first time
        if(!invoiceList) {
            let parameter = '?collected=True'
            if(action === "edit") {
                
                receipt = document.querySelector("#receipt-link").dataset.receipt;
                const ri = await getSubFields(
                    `/erp/api/sale_receipts/${receipt}`, ['related_invoice']
                );              

                parameter += `&exclude_inv_pk=${ri.related_invoice}`
                
            }
            invoiceList = await getList(`/erp/api/sale_invoices${parameter}`);
        }
        
        // Show or hide list after clicking on checkbox
        if(checked === false) {
            showCollectedInvoices(rInvoiceField, invoiceList);
            checked = true;
        } else {
            hideCollectedInvoices();
            checked = false;
        }
    
    });

})

async function autoSelectClient(relatedInvoice) {
    // get Client of related Invoice and pick the recipient
    
    const recipientField = document.querySelector("#id_recipient");
    const clientId = await getClientId(relatedInvoice);
    
    // Add it in recipient field 
    recipientField.value = clientId;

}

async function getClientId(relatedInvoice) {
    // Go to invoice api and extract client id

    const invoice = await getList('/erp/api/sale_invoices/' + relatedInvoice);
    return invoice.recipient;
        
}

function createCheckbox(parentElement) {
    // Create a checkbox for related invoice line.
    
    const checkBox = createElementComplete({
        tagName: 'form',
        innerHTML: `<label for="collected">Include collected invoices.</label>
        <input type="checkbox" id="id-collected" name="collected">`,
    });
    
    parentElement.append(checkBox);
    return checkBox;

}


function showCollectedInvoices(selectElement, invoiceList) {
    // Add to the list of related invoices those that were collected.

    invoiceList.forEach(invoice => {
        const optionElement = createElementComplete({
            tagName: 'option',
            attributeName: 'value',
            attributeValue: `${invoice.id}`,
            className: 'collected-inv',
            innerHTML: `${invoice.display_name}`,
        })
        
        selectElement.append(optionElement);
    })

}

function hideCollectedInvoices() {
    // Remove collected invoices.

    document.querySelectorAll(`.collected-inv`).forEach(element => 
        element.remove()
    );
    
}


