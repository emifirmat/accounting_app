document.addEventListener('DOMContentLoaded', function() {
    
    // Autoselect invoice number when pick a doc type and a pos
    const typeField = document.querySelector('#id_type');
    const posField = document.querySelector('#id_point_of_sell')
    
    typeField.addEventListener('change', () => {
        autoSelectNumber(typeField.value, posField.value);
    })
    posField.addEventListener('change', () => {
        autoSelectNumber(typeField.value, posField.value);
    })

    // Add a new line form for invoice
    const newLineButton = document.querySelector('#new-line')
    let lineFormIndex = parseInt(document.querySelector('#id_s_invoice_lines-TOTAL_FORMS').value, 10) - 1;
    
    newLineButton.addEventListener('click', () => {
        // Add new line, update index and total forms
        addNewLine(lineFormIndex);
        lineFormIndex++;
        document.querySelector('#id_s_invoice_lines-TOTAL_FORMS').value = lineFormIndex;
        
    }) 
        
})


async function autoSelectNumber(typeId, posId) {
    // Check last invoice of that type
    let lastInvoiceNumber;

    // Get and filter list
    if (typeId && posId) {
        const invoiceList = await getInvoiceList();
        const filteredList = filterList(typeId, posId, invoiceList);
        
        // If there's one invoice, select next number. Otherwise, return 1
        if (filteredList.length > 0) {
            lastInvoiceNumber = Math.max(...filteredList) + 1;
        } else {
            lastInvoiceNumber = 1;
        } 
    } else {
        // Return nothing as still there are fields to be picked
        return;
    }
    
    // Type on the field
    const numberField = document.querySelector('#id_number');
    numberField.value = lastInvoiceNumber;
}

function filterList(typeId, posId, invoiceList) {
    let filteredList = [];   
    
    // Filter with the type id
    for (const invoice of invoiceList) {
        // Only add invoices of this document type
        if (invoice.type == typeId && invoice.point_of_sell == posId) {
            filteredList.push(invoice.number);
        } 
    }

    return filteredList;
}

async function getInvoiceList() {
    // Get list of all invoices
    try {
        return fetch(`/erp/api/sale_invoices`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Couln't get the invoices list.");
            } else {
                return response.json();
            }
        })
    }
    catch (error) {
        console.error('Error' + error);
    }
}

function addNewLine (lineFormIndex) {
    // Add a new form
    
    const formSetSection = document.querySelector('#line-form-container');
    // Copy form template
    let lineFormTemplate = document.querySelector('#line-form-template').innerHTML;
    const newLineForm = lineFormTemplate.replace(/__prefix__/g, lineFormIndex);
    
    let divElement = document.createElement('div');
    divElement.className = "invoice-line";
    
    // Add template and update names
    divElement.innerHTML = `<br>${newLineForm}`;
    formSetSection.append(divElement);

}