document.addEventListener('DOMContentLoaded', async () => {

    // Get header sections (left and right sides)
    const headerSections = document.querySelectorAll('.headers');
 
    // Add the sorting event to each header
    headerSections.forEach(section => {
        const headers = Array.from(section.children);
        
        headers.forEach(header => header.addEventListener('click', event => {
            
            // Get CA list and parent element
            const curAccountListContainer = event.target.parentElement.nextElementSibling;
            const currentAccounts = curAccountListContainer.children;
            const column = event.target;

            // Sort the list according to the header
            const curAccountList = sortColumns(currentAccounts, headers, column, 'children');
            
            // Re-arrange list
            curAccountList.forEach(curAccount => 
                curAccountListContainer.append(curAccount));
        
        }));
    });

    // Manage settled accounts
    const hideButton = document.querySelector('#hide-tab');
    const textContent = ['Hide Settled Accounts', 'Unhide Settled Accounts'];
    let currentState = 0;

    hideButton.addEventListener('click', () => {
        
        // Hide and unhide settled accounts
        const totalCurrentAccounts = document.querySelectorAll('.specific-person');
        totalCurrentAccounts.forEach(account => {
            if (account.children[2].textContent === '$ 0.00') {
                account.classList.toggle('hidden');
            }
        })

        // Change tab
        currentState = 1 - currentState;
        hideButton.textContent = textContent[currentState];

    })
    
    // Add search client event
    const searchButton = document.querySelector('#search-tab');
    const clientList = await getSubFields('/erp/api/clients', ['name', 'tax_number'])

    searchButton.addEventListener('click', () =>    
        showSearchPopup(clientList)
    )


})

function showSearchPopup(clientList) {
    // Create and show popup
    const popContent = createElementComplete({
        tagName: 'div',
        className: 'person-list'
    })

    clientList.forEach(cClient => {
        const divElement = createElementComplete({
            tagName: 'div',
            className: 'person row',
            innerHTML: `<div class="col-8">${cClient.name}</div><div class="col-4">${cClient.tax_number}</div>`,
            eventName: 'click',
            eventFunction: () => window.location.href = `/erp/client/${cClient.id}/current_account`
        })
        popContent.append(divElement);
    });

    showPopUp('button', '', popContent, 'true');
    popupOneButton('Close');

}