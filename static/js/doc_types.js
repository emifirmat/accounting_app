document.addEventListener('DOMContentLoaded', () => showDocTypesList())

async function showDocTypesList() {
    // Show both visible and not visible doc types
    
    const vList = document.querySelector('#visible-list');
    const iList = document.querySelector('#invisible-list');

    try {       
        const dTList = await getList('/erp/api/document_types'); // crud.js
        
        // Clean old lists - Added here to make visual smoothier
        vList.innerHTML = '';
        iList.innerHTML = '';
    
        dTList.forEach(docType => addDocTypeToList(docType, vList, iList));
            
    } catch {
        console.error(`There was an error loading the document types. Please 
        contact the admin.`)
    }
}

function addDocTypeToList(docType, vList, iList) {
    
    // Create elements
    const spanElement = createElementComplete({
        tagName: 'span',
        className: 'row d-flex mb-2'
    });
    const buttonElement = createElementComplete({ // utils.js
        tagName: 'button',
        className:'col-4',
        eventName: 'click',
        eventFunction: event => changeDocTypeVisibility(docType, event)
    });
    const listItem = createElementComplete({ // utils.js
        tagName: 'li',
        className:'col-8',
        innerHTML: `${docType.code} | ${docType.description}`
    });

    // Set button content and location
    const textContent = docType.hide ? 'Unhide' : 'Hide';
    const dtList = docType.hide ? iList : vList;

    buttonElement.textContent = textContent;

    // Add elements
    spanElement.append(listItem, buttonElement);
    dtList.append(spanElement);

}

async function changeDocTypeVisibility(docType, event) {
    // Change doctype hide attribute
    
    const newHideStatus = !docType.hide;
    const vList = document.querySelector('#visible-list');
    const iList = document.querySelector('#invisible-list');

    try {
        
        const url = `/erp/api/document_types/${docType.id}`;
        await changeOneAttribute(url, 'hide', newHideStatus); // crud.js
        
        // Update docType.hide after updating the server
        docType.hide = newHideStatus;
        
        // Move element
        const buttonElement = event.target;
        const spanElement = buttonElement.parentElement;
        const targetList = newHideStatus ? iList : vList;

        // Change button
        buttonElement.textContent = newHideStatus ? 'Unhide' : 'Hide';
        targetList.append(spanElement);
        sortList(targetList);

    } catch {
        console.error(`Couldn't modify hidden status.`);
    }
    
}

function sortList(list) {
    
    // Sort list items by their content
    const items = Array.from(list.children);
    items.sort((a, b) => {
        const aText = a.querySelector('li').textContent.toLowerCase();
        const bText = b.querySelector('li').textContent.toLowerCase();
        return aText.localeCompare(bText);
    });

    // Re-append items in sorted order
    items.forEach(item => list.appendChild(item));
}
