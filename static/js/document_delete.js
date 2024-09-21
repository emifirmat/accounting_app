async function deleteComDocument(commercialDocument, cDocObject) {
    // Delete a specific document

    if (commercialDocument === "receipt") {
        cDocObject.type = "";
        var rTotalAmount = document.querySelector('#total-amount').dataset.amount;
    }

    const msg = `Are you sure you want to delete ${commercialDocument} ` +
        `${cDocObject.type} ${cDocObject.point_of_sell} - ${cDocObject.number}?`;
    
    const confirmDelete = confirm(msg.replace('  ', ' '));

    if(confirmDelete) {
        const deleteUrl = `/erp/api/sale_${commercialDocument}s/${cDocObject.id}`;
            
        await deleteInstance(deleteUrl, commercialDocument); // crud.js

        // If a receipt was deleted, update collected status in invoice
        if(commercialDocument === 'receipt' && rTotalAmount != 0) {
            
            const updateUrl = `/erp/api/sale_invoices/${cDocObject.related_invoice}`; // crud.js
            
            await changeOneAttribute(updateUrl, 'collected', false); // crud.js

        }
        
        // element to append the popup
        const mainSection = document.querySelector('main');

        let divElement = document.createElement('div');
        divElement.className = 'popup';
        divElement.innerHTML= `<span class="popuptext"> 
            The ${commercialDocument} has been deleted successfully.</span>`;
        divElement.addEventListener('animationend', () => {
            // Remove pop up
            divElement.remove();
        });
        
        mainSection.append(divElement);   
        
        return true;
        
    } else {
        return false;
    }
       
}