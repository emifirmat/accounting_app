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
    let invoiceList = await getInvoiceList();

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
        const pElement = document.createElement('p');
        pElement.innerHTML = "Couldn't match any invoice.";

        invoiceListSection.append(pElement);
    } else {
    
        for (let invoice of filteredInvoiceList) {
            // Create list item and buttons in html
            const liElement = document.createElement('li');
            const editButtonElement = document.createElement('button');
            const deleteButtonElement = document.createElement('button');

            // Buttons
            editButtonElement.innerHTML = "Edit";
            deleteButtonElement.innerHTML = "Delete";
            editButtonElement.className = "edit-button";
            deleteButtonElement.className = "delete-button";
            
            editButtonElement.addEventListener('click', () => {
                window.location.href = `/erp/sales/invoices/${invoice.id}/edit`;
            });
            deleteButtonElement.addEventListener('click', async () => {
                await deleteInvoice(invoice);
                setTimeout(() => location.reload(), 500);
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
        url = `/erp/api/document_types/`;
        return getSubField(url, typeId, result => 
            ({id: result.id, type: result.type}));
    }));   

    const posNumbers = await Promise.all(cleanedPosIdList.map(posId => {
        url = `/erp/api/points_of_sell/`;
        return getSubField(url, posId, result => 
            ({id: result.id, pos_number: result.pos_number}));
    }));
    // Get Clients name and tax number for each id
    const clientsInfo = await Promise.all(cleanedClientIdList.map(clientId => {
        url =`/erp/api/clients/`;
        return getSubField(url, clientId, result => 
        ({id: result.id, name: result.name, tax_number: result.tax_number}));
    }));

    return [typeTypes, posNumbers, clientsInfo];
}

async function getSubField(url, subFieldId, getResult) {
    // Take from API the subfield info
    try {
        return fetch(`${url}${subFieldId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Couldn't get pos number.");
            } else {
                return response.json();
            }
        })
        .then(result => getResult(result))
    } catch (error) {
        console.error(`Error trying to get ${url} for ID ${subFieldId}.`);
    }

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

