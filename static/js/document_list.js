document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('th').forEach(element => {
        element.addEventListener('click', event => {
            
            // Get comDocument information
            const comDocumentType = document.querySelector("#title").dataset["comDocument"];
            const docTypes = {'invoice': '.invoice', 'receipt': '.receipt'};
            const comDocuments = document.querySelectorAll(docTypes[comDocumentType]);

            getSortedComDocuments(event, comDocuments);
                        
        });
    });
});


function getSortedComDocuments(event, comDocuments) {
    // Sort and refresh invoices list
    
    const column = event.target;
    const columns = Array.from(document.querySelector('#columns').children);
    
    const sortedList = sortColumns(comDocuments, columns, column, 'cells');
   
    // Clean old list and add new com. documents
    const tableBody = document.querySelector('#table_body');
    sortedList.forEach(element => tableBody.append(element));

}