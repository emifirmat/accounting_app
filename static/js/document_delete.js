async function deleteComDocument(commercialDocument, cDocObject, redirectUrl) 
{
    // Delete a specific document

    if (commercialDocument === "receipt") {
        cDocObject.type = "";
        var rTotalAmount = await getSubFields(`/erp/api/sale_receipts/${cDocObject.id}`,
            result => result.total_amount
        );
    }
    
    const msg = generateDeleteMsg(commercialDocument, cDocObject);
    const confirmDelete = confirm(msg);

    // Stop function if alarm is canceled
    if(!confirmDelete) return false;
    
    const deleteUrl = `/erp/api/sale_${commercialDocument}s/${cDocObject.id}`;
           
    // Delete document or raise conflict pop up
    try {
        const deleted = await deleteInstance(deleteUrl, commercialDocument); // crud.js

        // Case of RestrictError.
        if(!deleted) {
            redirectUrl += `/invoices/${cDocObject.id}/related_receipts`;
            showPopUp('button', redirectUrl,
                `The invoice couldn't be deleted because there are some 
                receipts linked to it. Press Accept to delete or edit them.`
            );
            return false;
        }


        // If a receipt was deleted, update collected status in invoice
        if(commercialDocument === 'receipt' && rTotalAmount !== 0) {
    
            const updateUrl = `/erp/api/sale_invoices/${cDocObject.related_invoice}`; // crud.js
            await changeOneAttribute(updateUrl, 'collected', false); // crud.js

        }
        
        // element to append the popup
        showPopUp('animation', redirectUrl,
            `The ${commercialDocument} has been deleted successfully.`
        );
        
        return true;

    } catch {
        // If something wrong happened, stop the function.
        console.error(`Error deleting the ${commercialDocument}.`)
        return;

    }    
}

function showPopUp(mode, redirectUrl, content) {
    // If a receipt/invoice was deleted, show a pop up
    
    // element to append the popup
    const mainSection = document.querySelector('main');

    const divElement = createElementComplete({
        tagName: 'div',
        className: 'popup',
        innerHTML: `<span class="popup-text">${content}</span>`
    });      
    
    mainSection.append(divElement);

    if(mode == 'button') {
        // Use buttons
        
        divElement.style.animation = 'none';
        
        // New container for both buttons
        const newDivElement = createElementComplete({
            tagName: 'div',
            className: 'popup-footer',
        });

        divElement.append(newDivElement);

        ['Accept', 'Cancel'].forEach(element => {
            const buttonElement = createElementComplete({
                tagName: 'button',
                className: 'popup-button',
                innerHTML: element,
                eventName: 'click',
                eventFunction: () => 
                    redirectDelete(element, divElement, redirectUrl)
            });
            
            newDivElement.append(buttonElement);
        }) 

    } else if (mode == 'animation') {
        // Use animation and remove
        divElement.style.animationName = 'fadeIn';
        divElement.style.animationDuration = '3s';
        divElement.addEventListener('animationend', () => {
            if(redirectUrl) {
                window.location.href = redirectUrl;
            } else {
                location.reload();
            }
        })
    }
   
}

function generateDeleteMsg(commercialDocument, cDocObject) {
    // Msg for Delete confirmation, it makes code cleaner.
    
    msg = `Are you sure you want to delete ${commercialDocument} ` +
    `${cDocObject.type} ${cDocObject.point_of_sell} - ${cDocObject.number}?`;

    return msg.replace('  ', ' ');
}

function redirectDelete(button, divElement, redirectUrl) {
    // Redirect to invoice's related receipts.

    if(button === 'Accept') {
        window.location.href = redirectUrl;
    } else if (button === 'Cancel') {
        divElement.remove();
        return;
    }
}