document.addEventListener('DOMContentLoaded', function() {
    // After typing a letter in a field, search for matching invoices/receipts
    
    // Get document type
    const comDocument = document.querySelector('#search-title').dataset.document;
    
    // Get common fields
    const posField = document.querySelector('#id_pos');
    const numberField = document.querySelector('#id_number');
    const clientNameField = document.querySelector('#id_client_name');
    const clientTaxNumberField = document.querySelector('#id_client_tax_number');
    const yearField = document.querySelector('#id_year');
    const monthField = document.querySelector('#id_month');
    let searchFields = [posField, numberField, clientNameField, clientTaxNumberField,
        yearField, monthField];

    // Get particular fields
    let typeField = '';
    let rInvoiceField = '';
    if (comDocument === 'invoice') {
        typeField = document.querySelector('#id_type');
        searchFields.push(typeField);
    } else if (comDocument === 'receipt') {
        rInvoiceField = document.querySelector('#id_related_invoice');
        searchFields.push(rInvoiceField);
    }
    
    searchFields.forEach(field => {
        field.addEventListener('input', () => searchComDocuments(comDocument, 
            searchFields));
    });
 
});

async function searchComDocuments(comDocument, ...fields) {
    
    // Standarize fields
    const trimmedFields = fields[0].map(field => field.value.trim());
    
    // If all values are empty, hide list.
    const allEmpty = fields[0].every(field => field.value === '');
    if (allEmpty) {
        document.querySelector(`#${comDocument}-list`).innerHTML = '';
        return;
    }
    
    // Get the full list.
    let comDocumentList = await getList(`/erp/api/sale_${comDocument}s`); // crud.js

    // Get the subfields of each field
    let fieldsSubfields = await getCommonFieldsInfo(comDocumentList);
    fieldsSubfields.push(await getParticularFieldsInfo(comDocument, comDocumentList));
    
    // Convert invoice's ids fields
    comDocumentList = convertDocumentFields(comDocument, comDocumentList,
        fieldsSubfields);
    
    // Filter the list.
    const filteredCDocumentList = 
        filterCDocumentList(comDocument, comDocumentList, trimmedFields);

    // Show the list
    const cDocumentSection = document.querySelector(`#${comDocument}s-section`);
    const cDocumentListSection = document.querySelector(`#${comDocument}-list`);
    
    cDocumentSection.style.display = 'block';
    cDocumentListSection.innerHTML = '';
    
    if (filteredCDocumentList.length === 0) {
        const pElement = document.createElement('p');
        pElement.innerHTML = `Couldn't match any ${comDocument}.`;

        cDocumentListSection.append(pElement);
    } else {
    
        for (let cDocument of filteredCDocumentList) {
            // Create list item and buttons in html
            const liElement = document.createElement('li');
            const editButtonElement = document.createElement('button');
            const deleteButtonElement = document.createElement('button');

            // Buttons
            editButtonElement.innerHTML = "Edit";
            deleteButtonElement.innerHTML = "Delete";
            editButtonElement.className = "edit-button";
            deleteButtonElement.className = "delete-button";
            let baseUrl = '';
            let itemContent = '';

            if (comDocument === 'invoice') {
                baseUrl = `/erp/sales/invoices`;
                itemContent = `${cDocument.issue_date.substring(0, 10)} |
                 ${cDocument.type} | ${cDocument.point_of_sell}-${cDocument.number} |
                 ${cDocument.recipient} | ${cDocument.recipient_name}`
            } else if (comDocument === 'receipt') {
                baseUrl = `/erp/receivables/receipts`;
                itemContent = `${cDocument.issue_date.substring(0, 10)} | 
                ${cDocument.point_of_sell}-${cDocument.number} | 
                ${cDocument.recipient} | ${cDocument.recipient_name} |
                ${cDocument.related_invoice_info}`
            }
            
            editButtonElement.addEventListener('click', () => {
                window.location.href = `${baseUrl}/${cDocument.id}/edit`;
            });
            deleteButtonElement.addEventListener('click', async () => {
                if (await deleteComDocument(comDocument, cDocument)) { // document_delete.js
                    setTimeout(() => location.reload(), 500);
                }
            });

            // List item
            liElement.innerHTML = `<a href="${baseUrl}/${cDocument.id}">
            <p>${itemContent}</p></a>`;
            
            cDocumentListSection.append(liElement, editButtonElement,
                deleteButtonElement);
        }

    }
}

function filterCDocumentList(comDocument, cDocumentList, ...fields) {
    
    const filteredList = [];

    // Only add invoices/receipts with the following criteria
    for (const cDocument of cDocumentList) {
        
        // Determine last field depending on document being searched
        let particularField = '';
        if (comDocument === 'invoice') {
            particularField = cDocument.type;
        } else if (comDocument === 'receipt') {
            particularField = cDocument.related_invoice_info;
        }
        
        // Criteria
        if (
            String(cDocument.point_of_sell).includes(fields[0][0]) &&
            String(cDocument.number).includes(fields[0][1]) &&
            cDocument.recipient_name.toLowerCase().includes(fields[0][2].toLowerCase()) &&
            String(cDocument.recipient).includes(fields[0][3]) &&
            cDocument.issue_date.substring(0,4).includes(fields[0][4]) &&
            cDocument.issue_date.substring(5,7).includes(fields[0][5]) && 
            particularField.includes(fields[0][6].toUpperCase())
        ) {
            filteredList.push(cDocument);
        } 
    }

    return filteredList;
}


async function getCommonFieldsInfo(comDocumentList) {

    // Create a list of posIds and clientIds 
    const posIdList = comDocumentList.map(cDocument => cDocument.point_of_sell);
    const cleanedPosIdList = [...new Set(posIdList)];
    
    const clientIdList = comDocumentList.map(cDocument => cDocument.recipient);
    const cleanedClientIdList = [...new Set(clientIdList)];

    // Get pos numbers for each id
    const posNumbers = await Promise.all(cleanedPosIdList.map(posId => {
        return getSubFields(`/erp/api/points_of_sell/${posId}`, result => 
            ({id: result.id, pos_number: result.pos_number}));
    }));
    
    // Get Clients name and tax number for each id
    const clientsInfo = await Promise.all(cleanedClientIdList.map(clientId => {
        return getSubFields(`/erp/api/clients/${clientId}`, result => 
        ({id: result.id, name: result.name, tax_number: result.tax_number}));
    }));

    return [posNumbers, clientsInfo];

}

async function getParticularFieldsInfo(comDocument, comDocumentList) {
    // Create typeIds, and related_invoiceIds depending on the document
    if (comDocument === 'invoice') {

        const typeIdList = comDocumentList.map(invoice => invoice.type);
        const cleanedTypeIdList = [...new Set(typeIdList)];

        // Get invoice types for each id
        return await Promise.all(cleanedTypeIdList.map(typeId => {
            return getSubFields(`/erp/api/document_types/${typeId}`, result => 
                ({id: result.id, type: result.type}));
        }));
    } else if (comDocument === 'receipt') {
        const rInvoiceIdList = comDocumentList.map(receipt => receipt.related_invoice);
        const cleanedRInvoiceIdList = [...new Set(rInvoiceIdList)];

        // Get invoice type, pos and numbers for each id
        const relatedInvoice = await Promise.all(cleanedRInvoiceIdList.map(InvoiceId => {
            return getSubFields(`/erp/api/sale_invoices/${InvoiceId}`, result => 
                ({id: result.id, type: result.type, pos: result.point_of_sell,
                    number: result.number}));     
        }));
        // Convert pos and type id from related invoice to pos-number.
        for (let invoice of relatedInvoice) {
            invoice.type = await getSubFields(`/erp/api/document_types/${invoice.type}`,
                result => result.type);
            invoice.pos = await getSubFields(`/erp/api/points_of_sell/${invoice.pos}`,
                result => result.pos_number);   
        }
        
        return relatedInvoice;
    }
}

function convertDocumentFields(comDocument, cDocumentList, ...fieldsSubfields) {
    // Convert document attributes from id to real values 
    
    cDocumentList.forEach(cDocument => {

        // Common fields
        for (const posNumber of fieldsSubfields[0][0]) {
            if (posNumber.id === cDocument.point_of_sell) {
                cDocument.point_of_sell = posNumber.pos_number;
            }
        }

        for (const saleClient of fieldsSubfields[0][1]) {
            if (saleClient.id === cDocument.recipient) {
                cDocument.recipient = saleClient.tax_number;
                cDocument.recipient_name = saleClient.name;
            }
        }

        // particular fields
        if (comDocument === 'invoice') {
            for (const typeType of fieldsSubfields[0][2]) {
                if (typeType.id === cDocument.type) {
                    cDocument.type = typeType.type;
                }
            }
        } else if (comDocument === 'receipt') {
            for (const rInvoice of fieldsSubfields[0][2]) {
                if (rInvoice.id === cDocument.related_invoice) {
                    cDocument.related_invoice_info = 
                        `${rInvoice.type} ${rInvoice.pos}-${rInvoice.number}`;
                }
            }
        }
    });

    return cDocumentList;

}

