document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('th').forEach(function(element) {
        element.addEventListener('click', () => {
            
            // Get invoices information
            const invoices = document.querySelectorAll('.invoice');
            const columnIndex = event.target.dataset["col"];

            // Sort and refresh invoices list
            const invoice_list = sortInvoices(invoices, columnIndex);
            refreshList(invoice_list);
                        
        })    
    });
})


function sortInvoices(invoices, columnIndex) {
    
    // Get reverse info
    const column = document.querySelector('#columns');
    const reverse = column.children[columnIndex].dataset.reverse;
    
    // Convert node into an array for sorting
    const invoice_list = Array.from(invoices)
    
    // sort invoice list
    invoice_list.sort((a, b) => {
        // The list has all the rows with all the columns (w/o headers).
        // I select the cell of the column I clicked and use its text for sorting.
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Convert date column in dates for accurate comparison
        if(columnIndex == "0") {
            var aNotText = convertStringToDate(aText);
            var bNotText = convertStringToDate(bText);
        }
        
        // Convert total column content in float for accurate comparison
        if(columnIndex == "8") {
            var aNotText = parseFloat(aText.slice(2));
            var bNotText = parseFloat(bText.slice(2));
        }

        // If reverse is false, I sort in ascending order, otherwise desc.
        if(reverse === 'false') {
            column.children[columnIndex].dataset.reverse = 'true';
            // case: Date and Total amount
            if(columnIndex == "0" || columnIndex == "8") {
                return aNotText - bNotText
            } else {
                return aText.localeCompare(bText);
            }
        } else {
            column.children[columnIndex].dataset.reverse = 'false';
            if(columnIndex == "0" || columnIndex == "8") {
                return bNotText - aNotText
            } else {
                return bText.localeCompare(aText);
            }
        }
    })

    return invoice_list
}

function refreshList(invoice_list) {

    tableBody = document.querySelector('#table_body');
    // Clean old list and newone
    tableBody.innerHTML = '';
    invoice_list.forEach((element) => {
        tableBody.append(element)
    })
    
}

function convertStringToDate(string) {
    
    // Convert string to date
    dateArray = string.split('/');
    return Date.parse(`${dateArray[2]}-${dateArray[1]}-${dateArray[0]}`);
}