document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('th').forEach(function(element) {
        element.addEventListener('click', () => {
            
            // Get comDocument information
            const comDocumentType = document.querySelector("#title").dataset["comDocument"];
            let comDocuments;

            if(comDocumentType == 'invoice') {
                comDocuments = document.querySelectorAll('.invoice');
            } else if(comDocumentType == 'receipt') {
                comDocuments = document.querySelectorAll('.receipt');
            }

            getSortedComDocuments(comDocuments);
                        
        })    
    });
})


function getSortedComDocuments(comDocuments) {
    // Sort and refresh invoices list
    
    const column = event.target;
    const reverse = event.target.dataset.reverse;
    
    const comDocument_list = sortComDocuments(comDocuments, column, reverse);
    refreshList(comDocument_list);

}


function sortComDocuments(comDocuments, column, reverse) {
    
    // Get reverse info
    const columnName = column.dataset.col;
    const columns = Array.from(document.querySelector('#columns').children);
    const columnIndex = columns.indexOf(column);
     
    // Convert node into an array for sorting
    const comDocument_list = Array.from(comDocuments);
    
    // sort com. document list
    comDocument_list.sort((a, b) => {
        // The list has all the rows with all the columns (w/o headers).
        // I select the cell of the column I clicked and use its text for sorting.
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        
        // Convert date column in dates for accurate comparison
        if(columnName == "date") {
            var aNotText = convertStringToDate(aText);
            var bNotText = convertStringToDate(bText);
        }
        
        // Convert total column content in float for accurate comparison
        if(columnName == "total") {
            var aNotText = parseFloat(aText.slice(2));
            var bNotText = parseFloat(bText.slice(2));
        }

        // If reverse is false, I sort in ascending order, otherwise desc.
        if(reverse === 'false') {
            column.dataset.reverse = 'true';
            // case: Date and Total amount
            if(columnName == "date" || columnName == "total") {
                return aNotText - bNotText;
            } else {
                return aText.localeCompare(bText);
            }
        } else {
            column.dataset.reverse = 'false';
            if(columnName == "date" || columnName == "total") {
                return bNotText - aNotText;
            } else {
                return bText.localeCompare(aText);
            }
        }
    })

    return comDocument_list
}

function refreshList(comDocument_list) {

    tableBody = document.querySelector('#table_body');
    // Clean old list and add new com. documents
    tableBody.innerHTML = '';
    comDocument_list.forEach((element) => {
        tableBody.append(element);
    })
    
}

function convertStringToDate(string) {
    
    // Convert string to date
    dateArray = string.split('/');
    return Date.parse(`${dateArray[2]}-${dateArray[1]}-${dateArray[0]}`);
}