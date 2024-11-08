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
    
    const searchFields = [posField, numberField, clientNameField, clientTaxNumberField,
        yearField, monthField];

    // Get particular fields
    let collectedField, typeField;
    let rInvoiceField;

    if (comDocument === 'invoice') {
        typeField = document.querySelector('#id_type');
        collectedField = document.querySelector('#id_collected');
        searchFields.push(typeField);
        
        collectedField.addEventListener('change', async () => {
            // Each option fetches a different list of invoices
            comDocumentList = await preloadComDocuments(comDocument, 
                comDocumentList, collectedField);
            searchComDocuments(comDocument, comDocumentList, searchFields);
        });
    
    } else if (comDocument === 'receipt') {
        rInvoiceField = document.querySelector('#id_related_invoice');
        searchFields.push(rInvoiceField);
    }
    
    // list cache, to make searching faster
    let comDocumentList;
    
    searchFields.forEach(field => {
        field.addEventListener('focus', async () => {
            // preload fetch list when user clicks on a field for the first time.
            if (!comDocumentList) {
                comDocumentList = await preloadComDocuments(
                    comDocument, comDocumentList, collectedField
                )
            }
        })
    
        field.addEventListener('input', async () => { 
            // Get cache from comDocList but fetch list again if focus didn't word.
            // Then Search and show documents from the list according to the filters.
            if (!comDocumentList) {
                comDocumentList = await preloadComDocuments(
                    comDocument, comDocumentList, collectedField
                )
            }
            
            searchComDocuments(comDocument, comDocumentList, searchFields)
        })
    });
});

async function preloadComDocuments(comDocument, comDocumentList, collectedField) {
    // Preload the invoices to allow fast searching
    
    // Get the list.
    let url = `/erp/api/sale_${comDocument}s`;
    if (comDocument === 'invoice') {
        let collectedStatus = collectedField.value;
        if(collectedStatus === 'op1') {
            collectedStatus = '';
        } else if (collectedStatus === 'op2') {
            collectedStatus = 'false';
        } else {
            collectedStatus = 'true';
        }
        url += `?collected=${collectedStatus}`
    }

    comDocumentList = await getList(url);

    // Get the subfields of each field
    const fieldsSubfields = await Promise.all([
        getCommonFieldsInfo(comDocumentList),
        getParticularFieldsInfo(comDocument, comDocumentList)
    ]);

    // Convert invoice's ids fields
    comDocumentList = convertDocumentFields(comDocument, comDocumentList,
        fieldsSubfields);

    return comDocumentList;

}

function searchComDocuments(comDocument, comDocumentList, ...fields) {
    // Search com documents from the full list
    
    // Standarize fields
    const trimmedFields = fields[0].map(field => field.value.trim());
    
    // If all values are empty, hide list.
    const allEmpty = fields[0].every(field => field.value === '');
    if (allEmpty) {
        document.querySelector(`#search-headers`).innerHTML = '';
        document.querySelector(`#search-rows`).innerHTML = '';
        return;
    }   

    // Filter the list.
    const filteredCDocumentList = 
        filterCDocumentList(comDocument, comDocumentList, trimmedFields);

    // Show the list
    const cDocumentSection = document.querySelector(`#${comDocument}s-section`);
    const searchHeaders = document.querySelector(`#search-headers`);
    const searchRows = document.querySelector(`#search-rows`);
    
    cDocumentSection.style.display = 'block';
    searchHeaders.innerHTML = '';
    searchRows.innerHTML = '';
    
    if (filteredCDocumentList.length === 0) {
        const pElement = createElementComplete({
            tagName: 'p',
            innerHTML: `Couldn't match any ${comDocument}.`
        });

        searchRows.append(pElement);
    } else {

        // Add headers
        let headers;
        if (comDocument === 'invoice') {
            headers = ['Issue Date', 'Type', 'Number', 'Recipient Tax Number', 
                'Recipient Name', 'Collected'];
        } else if (comDocument === 'receipt') {
            headers = ['Issue Date', 'Number', 'Recipient Tax Number',
                'Recipient Name', 'Related Invoice'];
        }
        
        createHeaders(searchHeaders, headers);
        
        
        for (let cDocument of filteredCDocumentList) {
            // Create list item and buttons in html     
            let baseUrl = '';
            let itemContent = '';
            let gridColumns = '';
           
            if (comDocument === 'invoice') {
                // Set columns (add space for the buttons)
                gridColumns = '2fr 1fr 2fr 2fr 2fr 1fr 1fr 1fr 1fr'
                searchHeaders.style.gridTemplateColumns = gridColumns;
                
                baseUrl = `/erp/sales`;
                endUrl = `/invoices/${cDocument.id}`
                itemContent = `
                <div class=search-cell>${cDocument.issue_date.substring(0, 10)}</div>
                <div class=search-cell>${cDocument.type}</div>
                <div class=search-cell>${cDocument.point_of_sell}-${cDocument.number}</div>
                <div class=search-cell>${cDocument.recipient}</div>
                <div class=search-cell>${cDocument.recipient_name}</div>
                <div class=search-cell>${cDocument.collected}</div>`
            
            } else if (comDocument === 'receipt') {
                // Set columns (add space for the buttons)
                gridColumns = '2fr 2fr 2fr 2fr 2fr 1fr 1fr 1fr'
                searchHeaders.style.gridTemplateColumns = gridColumns;

                baseUrl = `/erp/receivables`;
                endUrl = `/receipts/${cDocument.id}`
                itemContent = `
                <div class=search-cell>${cDocument.issue_date.substring(0, 10)}</div> 
                <div class=search-cell>${cDocument.point_of_sell}-${cDocument.number}</div>
                <div class=search-cell>${cDocument.recipient}</div> 
                <div class=search-cell>${cDocument.recipient_name}</div>
                <div class=search-cell>${cDocument.related_invoice_info}</div>`
            }

            const rowElement = createElementComplete({
                tagName: 'div',
                className: 'search-row',
                innerHTML: itemContent
            })
            // Set columns (headers + buttons) for rows
            rowElement.style.gridTemplateColumns = gridColumns

            const viewButtonElement = createElementComplete({
                tagName: 'button',
                innerHTML: `View`,
                className: 'view-button',
                eventName: 'click',
                eventFunction: () =>
                    window.location.href = `${baseUrl}${endUrl}`
            });
            const editButtonElement = createElementComplete({
                tagName: 'button',
                innerHTML: 'Edit',
                className: 'edit-button',
                eventName: 'click',
                eventFunction: () => 
                    window.location.href = `${baseUrl}${endUrl}/edit`
            });
            const deleteButtonElement = createElementComplete({
                tagName: 'button',
                innerHTML: 'Delete',
                className: 'delete-button',
                eventName: 'click',
                eventFunction: async () => 
                    // document_delete.js
                    await deleteComDocument(comDocument, cDocument, baseUrl)
            });
            
            // Append created elements
            rowElement.append(viewButtonElement, editButtonElement,
                deleteButtonElement);

            searchRows.append(rowElement)
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
    let posIdList = comDocumentList.map(cDocument => cDocument.point_of_sell);
    posIdList = [...new Set(posIdList)];
    
    let clientIdList = comDocumentList.map(cDocument => cDocument.recipient);
    clientIdList = [...new Set(clientIdList)];

    // Get pos numbers and clients tax and name for each id in parallel mode.
    const [posNumbers, clientsInfo] = await Promise.all([

        Promise.all(posIdList.map(posId => 
            getSubFields(`/erp/api/points_of_sell/${posId}`, ['id', 'pos_number'])
        )),
        
        Promise.all(clientIdList.map(clientId => 
            getSubFields(
                `/erp/api/clients/${clientId}`, ['id', 'name', 'tax_number']
            )
        ))
    ])

    return [posNumbers, clientsInfo];

}

async function getParticularFieldsInfo(comDocument, comDocumentList) {
    // Create typeIds, and related_invoiceIds depending on the document
    if (comDocument === 'invoice') {

        let typeIdList = comDocumentList.map(invoice => invoice.type);
        typeIdList = [...new Set(typeIdList)];

        // Get invoice types for each id
        return await Promise.all(typeIdList.map(typeId => 
            getSubFields(
                `/erp/api/document_types/${typeId}`, ['id', 'type'])
            )
        );
    } else if (comDocument === 'receipt') {
        let rInvoiceIdList = comDocumentList.map(receipt => receipt.related_invoice);
        rInvoiceIdList = [...new Set(rInvoiceIdList)];

        // Get invoice name
        let relatedInvoices = await Promise.all(rInvoiceIdList.map(InvoiceId => 
            getSubFields(
                `/erp/api/sale_invoices/${InvoiceId}`, ['id', 'display_name']
            )
        ));

        return relatedInvoices;
    }
}

function convertDocumentFields(comDocument, cDocumentList, fieldsSubfields) {
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
            for (const typeType of fieldsSubfields[1]) {
                if (typeType.id === cDocument.type) {
                    cDocument.type = typeType.type;
                }
            }
        } else if (comDocument === 'receipt') {
            for (const rInvoice of fieldsSubfields[1]) {
                if (rInvoice.id === cDocument.related_invoice) {
                    cDocument.related_invoice_info = rInvoice.display_name;
                }
            }
        }
    });

    return cDocumentList;

}

function createHeaders(container, headers) {
    // Create headers for search section

    // Create headers
    headers.forEach(header => {
        const element = createElementComplete({
            tagName: 'div',
            innerHTML: header.toUpperCase(),
            className: 'header'
        });
        container.append(element);
    })

}