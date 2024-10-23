document.addEventListener('DOMContentLoaded', function() {

    // Add functinoality to buttoms
    document.querySelectorAll('.default-button').forEach(function (element) {
        element.addEventListener('click', () => addDefault());
    });
    document.querySelectorAll('.add-button').forEach(function (element) {
        element.addEventListener('click', () => newCondition());
    });
    document.querySelectorAll('.view-button').forEach(function (element) {
        element.addEventListener('click', () => showCondition());
    });
});

function addDefault() {
    event.preventDefault()
    
    // Add default rows to db
    const confirmDefault = confirm('Load default?');
    const pCondition = event.target.parentNode.parentNode.dataset.section;


    if (confirmDefault) {
        let data;
        if (pCondition === 'method') {
            data = [
                {'pay_method': 'Cash'}, 
                {'pay_method': 'Transfer'},
                {'pay_method': 'Check'}
            ];
        } else if (pCondition === 'term') {
            data = [
                {'pay_term': '0'}, 
                {'pay_term': '15'}, 
                {'pay_term': '30'}, 
                {'pay_term': '60'}
            ];
        } else {
            console.error('Check dataset');
            return;
        }

        // Create api point and pass it through fetch
        const url = `/erp/api/payment_conditions/${pCondition}s`;
        postData(url, data, "Default loaded successfully."); // crud.js
        
        document.querySelector('#message-section').innerHTML = `<p>Default 
            for ${pCondition} loaded successfully.</p>`;
            setTimeout(() => location.reload(), 1000);
    }
}

function newCondition() {
    // Show form and add functionality
    const pCondition = event.target.parentNode.dataset.section;
    console.log(pCondition)
    let newSection = document.querySelector(`#new-${pCondition}`)
    
    newSection.style.display = 'block';
    newSection.querySelector('button').addEventListener('click', () =>
        confirmNewCondition(newSection, pCondition))
}

function confirmNewCondition(newSection, pCondition) {
    // Add new entry to db
    event.preventDefault()
    
    const confirmNew = confirm(`Add new ${pCondition}?`);
    
    if (confirmNew) {
        let data;
        const form = newSection.children[0];
        if (pCondition === 'method') {
            data = {'pay_method': form.elements[`pay_${pCondition}`].value};
            console.log(data)
        } else if (pCondition === 'term') {
            data = {'pay_term': form.elements[`pay_${pCondition}`].value};
            console.log(data)
        } else {
            console.error('Check dataset');
            return;
        }

        // Create api point a pass it through fetch
        const url = `/erp/api/payment_conditions/${pCondition}s`;
        postData(url, data, 'New ${pCondition} added successfully.'); // crud.js
        
        document.querySelector('#message-section').innerHTML = `<p>New 
        ${pCondition} added successfully.</p>`;
        setTimeout(() => location.reload(), 1000);
    }
}


async function showCondition(pCondition = '') {
    // Get payment term or method list
    if (!pCondition) {
        var pCondition = event.target.parentNode.dataset.section;
    }

    // Get list through fetch
    const url = `/erp/api/payment_conditions/${pCondition}s`;
    const pConditionList = await getList(url); // crud.js
  
    // Refresh page if there aren't any values
    if(!pConditionList.length) {
        location.reload();
    } else {
        // Add title
        const sectionTitle = document.querySelector('#view-title');
        sectionTitle.innerHTML = `Payment ${pCondition}s:`;
        
        // Add all elements of the list
        const sectionList = document.querySelector('#view-list');
        sectionList.innerHTML = '';

        pConditionList.forEach(item => {
            const listItem = document.createElement('li');
            
            // Customize item
            if (pCondition === "method") {
                listItem.innerHTML = item.pay_method;
            } else if (pCondition === "term") {
                listItem.innerHTML = item.pay_term;
            }

            // Customize delete button
            const deleteButton = createElementComplete({
                tagName: 'button',
                className: 'delete-item',
                innerHTML: 'Delete',
                eventName: 'click',
                eventFunction: () => {
                    // Ask for confirmation in the button
                    deleteButton.innerHTML = "Confirm";
                    deleteButton.addEventListener('click', () => deleteItem(
                        item.id, pCondition));
                }
            });
            
            sectionList.append(listItem, deleteButton);
        })
    }
} 

async function deleteItem(itemId, pCondition) {
    
    // Delete an item of the list
    const url = `/erp/api/payment_conditions/${pCondition}s/${itemId}`;
    
    await deleteInstance(url, pCondition); // crud.js
    
    showCondition(pCondition);
}
