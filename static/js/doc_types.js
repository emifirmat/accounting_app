document.addEventListener('DOMContentLoaded', function () {
    showDocTypesList();
})

async function showDocTypesList() {
    // Show both visible and not visible doc types
    const dTList = await getDocTypes();
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


function changeDocTypeVisibility(docTypeId, hideStatus) {
    // Change doctype hide attribute
    if (hideStatus === true) {
        hideStatus = false;
    } else {
        hideStatus = true;
    }

    try {
        fetch(`/erp/api/document_types/${docTypeId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hide: hideStatus,
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Couldn't change doc type visibility.");
            } else {
                console.log("Visibility changed successfully.");
                showDocTypesList();
            }
        })
    } 
    catch (error) {
        console.error('Error', error);
    }
}

async function getDocTypes() {
    // Get list of DocTypes
    try {
        return fetch('/erp/api/document_types')
        .then(response => {
            if (!response.ok) {
                throw new Error("Couldn't load document types list.");
            } else {
                return response.json();
            }
        })
    }
    catch(error) {
        console.error('Error', error);
    }
}