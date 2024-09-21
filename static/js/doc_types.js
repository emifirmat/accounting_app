document.addEventListener('DOMContentLoaded', function () {
    // Show both visible and not visible doc types

    showDocTypesList();

})

async function showDocTypesList() {
    // Show both visible and not visible doc types
    const dTList = await getList('/erp/api/document_types'); // crud.js
    const vList = document.querySelector('#visible-list');
    const iList = document.querySelector('#invisible-list');

    // Clean old lists
    vList.innerHTML = '';
    iList.innerHTML = '';

    for (const docType of dTList) {
        const buttonElement = document.createElement('button');
        const spanElement = document.createElement('span');
        const listItem = document.createElement('li');
        listItem.innerHTML = `${docType.code} | ${docType.type_description}`;
        
        buttonElement.addEventListener('click', () =>
            changeDocTypeVisibility(docType.id, docType.hide));
        spanElement.append(listItem, buttonElement);

        if (docType.hide === false) {
            buttonElement.innerHTML = 'Hide';
            vList.append(spanElement);
        } else {
            buttonElement.innerHTML = 'Unhide';
            iList.append(spanElement);
        }
    }
}


async function changeDocTypeVisibility(docTypeId, hideStatus) {
    // Change doctype hide attribute
    const url = `/erp/api/document_types/${docTypeId}`;
    if (hideStatus === true) {
        hideStatus = false;
    } else {
        hideStatus = true;
    }

    await changeOneAttribute(url, 'hide', hideStatus); // crud.js

    showDocTypesList();
    
}
