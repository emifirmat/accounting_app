async function deleteInvoice(invoice) {
    // Delete a specific invoice
    return new Promise((resolve, reject) => {
        const confirmDelete = confirm(
            `Are you sure you want to delete invoice ${invoice.type} ${invoice.point_of_sell} - ${invoice.number}?`
        );
    
        if(confirmDelete) {
            try {
                fetch(`/erp/api/sale_invoices/${invoice.id}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Couldn't delete the invoice.");
                    } else {
                        // Create pop up of confirmation
                        console.log('Invoice has been deleted successfully.');
    
                        // element to append the popup
                        const mainSection = document.querySelector('main');
    
                        let divElement = document.createElement('div');
                        divElement.className = 'popup';
                        divElement.innerHTML= `<span class="popuptext"> 
                            Invoice has been deleted successfully.</span>`;
                        divElement.addEventListener('animationend', () => {
                            // Remove pop up
                            divElement.remove();
                            return resolve();
                        });
                        
                        mainSection.append(divElement);         
                        
                    }
                })
            }
            catch (error) {
                console.error('Error' + error);
            }
        }


    })
    
}