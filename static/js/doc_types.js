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
        const spanElement = document.createElement('span');
        const buttonElement = createElementComplete({ // utils.js
            tagName: 'button',
            eventName: 'click',
            eventFunction: () => changeDocTypeVisibility(docType.id, docType.hide),
        });
        const listItem = createElementComplete({ // utils.js
            tagName: 'li',
            innerHTML: `${docType.code} | ${docType.type_description}`
        })

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
