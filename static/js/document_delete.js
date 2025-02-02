async function deleteComDocument(commercialDocument, cDocObject, redirectUrl) 
{
    // Delete a specific document

    if (commercialDocument === "receipt") {
        cDocObject.type = "";
        var rTotalAmount = await getSubFields(
            `/erp/api/sale_receipts/${cDocObject.id}`, ['total_amount']
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

async function deleteMultipleDocuments(commercialDocument, selectedIds, redirectUrl){

    const confirmDelete = confirm(
        `Are you sure you want to delete ${selectedIds.size} ${commercialDocument}s?`
    );
        
    // Stop function if alarm is canceled
    if(!confirmDelete) return false;

    // Delete document or raise conflict pop up
    try {
        const deleteUrl = `/erp/api/sale_${commercialDocument}s/bulk_delete`;
        let relatedInvoices;
        selectedIds = Array.from(selectedIds);

        if (commercialDocument === 'receipt') {
            
            // Get necessary data before deleting the receipt
            relatedInvoices = await Promise.all(selectedIds.map(receiptId => 
                getSubFields(
                    `/erp/api/sale_receipts/${receiptId}`,
                    ['total_amount', 'related_invoice']
                )
            ))
        
        }
       

        const deleted = await deleteInstance(deleteUrl, commercialDocument, selectedIds); // crud.js

        // Case of RestrictError.
        if(!deleted) {
            showPopUp('button', '',
                `The selected invoices couldn't be deleted because there are some 
                receipts linked to one or more of them.`
            );
            // Alter button style
            popupOneButton()
            return false;
        }

        // element to append the popup
        showPopUp('animation', redirectUrl,
            `The ${commercialDocument}s have been deleted successfully.`
        );
        
        return true;

    } catch {
        // If something wrong happened, stop the function.
        console.error(`Error deleting the ${commercialDocument}s.`)
        return;

    }    


}



function generateDeleteMsg(commercialDocument, cDocObject) {
    // Msg for Delete confirmation, it makes code cleaner.
    
    msg = `Are you sure you want to delete ${commercialDocument} ` +
    `${cDocObject.type} ${cDocObject.point_of_sell} - ${cDocObject.number}?`;

    return msg.replace('  ', ' ');
}

