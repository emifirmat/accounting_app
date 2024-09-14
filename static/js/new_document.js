document.addEventListener('DOMContentLoaded', () => {

    // Autoselect invoice number when pick a doc type and a pos
    const posField = document.querySelector('#id_point_of_sell')
    const documentType = document.querySelector('#document-title').dataset.document;

    if(documentType === "invoice") {
        const typeField = document.querySelector('#id_type');
        typeField.addEventListener('change', () => {
            autoSelectNumber(documentType, posField.value, typeField.value);
        });
        posField.addEventListener('change', () => {
            autoSelectNumber(documentType, posField.value, typeField.value);
        });
    } else {
        posField.addEventListener('change', () => {
            autoSelectNumber(documentType, posField.value);
        });
    };
})

async function autoSelectNumber(documentType, ...fieldsIds) {
    // Check last invoice(or receipt) of the same type and pos
    let lastDocumentNumber;
    let filteredList;

    // Get and filter list
    if (
        (documentType === 'invoice' && fieldsIds[0] && fieldsIds[1]) || 
        (documentType === 'receipt' && fieldsIds[0])
    ) {
        // fields[0] = pos | fields [1] = type
        const documentList = await getDocumentList(`sale_${documentType}`, documentType);
        filteredList = filterList(documentType, documentList, ...fieldsIds);
    } else {
        // Return nothing as still there are fields to be picked
        return;
    }

    // If there's one invoice (or receipt), select next number. Otherwise, return 1
    if (filteredList.length > 0) {
        lastDocumentNumber = Math.max(...filteredList) + 1;
    } else {
        lastDocumentNumber = 1;
    } 
    
    // Type on the field
    const numberField = document.querySelector('#id_number');
    numberField.value = lastDocumentNumber;
}

function filterList(documentType, documentList, ...fieldsIds) {
    
    // Filter with the type id
    let filteredList = documentList.filter(commercialDocument => {
        // Only add invoices of this document type
        if (documentType === "invoice") {
            return commercialDocument.point_of_sell == fieldsIds[0] && commercialDocument.type == fieldsIds[1]
        } else {
            // Only add invoices of this document type
            return commercialDocument.point_of_sell == fieldsIds[0]
        } 
    });

    return filteredList.map(commercialDocument => commercialDocument.number);

}

async function getDocumentList(url, document) {
    // Get list of all documents
    try {
        return fetch(`/erp/api/${url}s`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Couldn't get the ${document} list.`);
            } else {
                return response.json();
            }
        })
    }
    catch (error) {
        console.error('Error' + error);
    }
}