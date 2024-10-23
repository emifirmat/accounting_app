document.addEventListener('DOMContentLoaded', function() {

    // After typing a letter in a field, search for matching invoices
    const typeField = document.querySelector('#id_type');
    const posField = document.querySelector('#id_pos');
    const numberField = document.querySelector('#id_number');
    const clientNameField = document.querySelector('#id_client_name');
    const clientTaxNumberField = document.querySelector('#id_client_tax_number');
    const yearField = document.querySelector('#id_year');
    const monthField = document.querySelector('#id_month');
    
    function takeFieldsValues() {
        searchInvoices(
            typeField.value, posField.value, numberField.value, 
            clientNameField.value, clientTaxNumberField.value, yearField.value,
            monthField.value
        );
    }
    
    typeField.addEventListener('input', takeFieldsValues);
    posField.addEventListener('input', takeFieldsValues);
    numberField.addEventListener('input', takeFieldsValues);
    clientNameField.addEventListener('input', takeFieldsValues);
    clientTaxNumberField.addEventListener('input', takeFieldsValues);
    yearField.addEventListener('input', takeFieldsValues);
    monthField.addEventListener('input', takeFieldsValues);
 
});

async function searchInvoices(...fields) {
    
    // Standarize fields
    const trimmedFields = fields.map(field => field.trim());
    // If all values are empty, hide list.
    const allEmpty = fields.every(value => value === '');
    if (allEmpty) {
        document.querySelector('#invoice-list').innerHTML = '';
        return;
    }
    
    // Get the full list.
    let invoiceList = await getList('/erp/api/sale_invoices'); // crud.js

    // Get the subfields of each field
    const [typeTypes, posNumbers, clientsInfo] = await getFieldsInfo(invoiceList);

    // Convert invoice's ids fields
    invoiceList = convertInvoiceFields(invoiceList, typeTypes, posNumbers,
        clientsInfo);
    
    // Filter the list.
    const filteredInvoiceList = 
        filterInvoiceList(invoiceList, trimmedFields);

    // Show the list
    const invoicesSection = document.querySelector('#invoices-section');
    const invoiceListSection = document.querySelector('#invoice-list');
    
    invoicesSection.style.display = 'block';
    invoiceListSection.innerHTML = '';
    
    if (filteredInvoiceList.length === 0) {
        const pElement = createElementComplete({
            tagName: 'p',
            innerHTML: "Couldn't match any invoice."
        });

        invoiceListSection.append(pElement);
    } else {
    
        for (let invoice of filteredInvoiceList) {
            // Create list item and buttons in html
            const liElement = document.createElement('li');
            const editButtonElement = createElementComplete({ // utils.js
                tagName: 'button',
                innerHTML: 'Edit',
                className: 'edit-button',
                eventName: 'click',
                eventFunction: () =>
                    window.location.href = `/erp/sales/invoices/${invoice.id}/edit`
            });
            const deleteButtonElement = createElementComplete({ 
                tagName: 'button',
                innerHTML: 'Delete',
                className: 'delete-button',
                eventName: 'click',
                eventFunction: async () => 
                    await deleteComDocument('invoice', invoice) // document_delete.js
            });

            // List item
            liElement.innerHTML = `<a href="/erp/sales/invoices/${invoice.id}">
            <p>${invoice.issue_date.substring(0, 10)} | ${invoice.type} | 
            ${invoice.point_of_sell} | ${invoice.number} | ${invoice.recipient} | 
            ${invoice.recipient_name}</p></a>`;
            
            invoiceListSection.append(liElement, editButtonElement,
                deleteButtonElement);
        }

    }
}

function filterInvoiceList(invoiceList, ...fields) {
    
    const filteredList = [];

    // Filter with the type id
    for (const invoice of invoiceList) {
        // Only add invoices of this document type
        if (
            String(invoice.type).includes(fields[0][0].toUpperCase()) &&
            String(invoice.point_of_sell).includes(fields[0][1]) &&
            String(invoice.number).includes(fields[0][2]) &&
            invoice.recipient_name.toLowerCase().includes(fields[0][3].toLowerCase()) &&
            String(invoice.recipient).includes(fields[0][4]) &&
            invoice.issue_date.substring(0,4).includes(fields[0][5]) &&
            invoice.issue_date.substring(5,7).includes(fields[0][6])

        ) {
            filteredList.push(invoice);
        } 
    }

    return filteredList;
}


async function getFieldsInfo(invoiceList) {

    // Create a list of typeIds, posIds and clientIds
    const typeIdList = invoiceList.map(invoice => invoice.type);
    const cleanedTypeIdList = [...new Set(typeIdList)];
    
    const posIdList = invoiceList.map(invoice => invoice.point_of_sell);
    const cleanedPosIdList = [...new Set(posIdList)];
    
    const clientIdList = invoiceList.map(invoice => invoice.recipient);
    const cleanedClientIdList = [...new Set(clientIdList)];

    // Get Pos numbers for each id
    const typeTypes = await Promise.all(cleanedTypeIdList.map(typeId => {
        return getSubField(`/erp/api/document_types/`, typeId, result => 
            ({id: result.id, type: result.type}));
    }));   

    // Get pos numbers for each id
    const posNumbers = await Promise.all(cleanedPosIdList.map(posId => {
        return getSubField(`/erp/api/points_of_sell/`, posId, result => 
            ({id: result.id, pos_number: result.pos_number}));
    }));
    
    // Get Clients name and tax number for each id
    const clientsInfo = await Promise.all(cleanedClientIdList.map(clientId => {
        return getSubField(`/erp/api/clients/`, clientId, result => 
        ({id: result.id, name: result.name, tax_number: result.tax_number}));
    }));

    return [typeTypes, posNumbers, clientsInfo];
}

async function getSubField(url, subFieldId, getResult) {
    // Take from API the subfield info
    
    const subField = await getList(`${url}${subFieldId}`); // crud.js
    
    return getResult(subField);

}

function convertInvoiceFields(invoiceList, typeTypes, posNumbers, clientsList) {
    // Convert invoice attributes from id to real values 
      
    invoiceList.forEach(invoice => {
        for (const typeType of typeTypes) {
            if (typeType.id === invoice.type) {
                invoice.type = typeType.type;
            }
        }
        
        for (const posNumber of posNumbers) {
            if (posNumber.id === invoice.point_of_sell) {
                invoice.point_of_sell = posNumber.pos_number;
            }
        }

        for (const client of clientsList) {
            if (client.id === invoice.recipient) {
                invoice.recipient = client.tax_number;
                // Add recipient name attribute in lower case for insensitive search
                invoice.recipient_name = client.name;
            }
        }
    });

    return invoiceList;

}

