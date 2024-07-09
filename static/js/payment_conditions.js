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

        // Create api point a pass it through fetch
        const csrftoken = getCookie('csrftoken');
        fetch(`/erp/api/payment_conditions/${pCondition}s`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            mode: "same-origin"
        })
        .then(response => ({
            status: response.status,
            ok: response.ok,
        }))
        .then(result => {
            if (result.ok) {
                console.log('Default loaded successfully.');
                document.querySelector('#message-section').innerHTML = `<p>Default 
                for ${pCondition} loaded successfully.</p>`;
                setTimeout(() => location.reload(), 1000);
            } else {
                console.error("Default couldn't load");
            }
        })
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
        const csrftoken = getCookie('csrftoken');
        fetch(`/erp/api/payment_conditions/${pCondition}s`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            mode: "same-origin"
        })
        .then(response => ({
            status: response.status,
            ok: response.ok,
        }))
        .then(result => {
            if (result.ok) {
                console.log(`New ${pCondition} added successfully.`);
                document.querySelector('#message-section').innerHTML = `<p>New 
                ${pCondition} added successfully.</p>`;
                setTimeout(() => location.reload(), 1000);
            } else {
                console.error(`Error while adding a new ${pCondition}`);
            }
        })
    }
}


function showCondition(pCondition = '') {
    // Get payment term or method list
    if (!pCondition) {
        var pCondition = event.target.parentNode.dataset.section;
    }

    // Get list through fetch
    fetch(`/erp/api/payment_conditions/${pCondition}s`)
    .then(response => {
        if (!response) {
            throw new Error("Couldn't get the list");
        } else {
            return response.json();
        }
    })
    .then(result => {   
        // Refresh page if there aren't any values
        if(!result.length) {
           location.reload();
        } else {
            // Add title
            const sectionTitle = document.querySelector('#view-title');
            sectionTitle.innerHTML = `Payment ${pCondition}s:`;
            
            // Add all elements of the list
            const sectionList = document.querySelector('#view-list');
            sectionList.innerHTML = '';

            result.forEach(item => {
                const listItem = document.createElement('li');
                let deleteButton = document.createElement('button');
                
                // Customize item
                if (pCondition === "method") {
                    listItem.innerHTML = item.pay_method;
                } else if (pCondition === "term") {
                    listItem.innerHTML = item.pay_term;
                }

                // Customize delete button
                deleteButton.className = 'delete-item';
                deleteButton.innerHTML = 'Delete';
                deleteButton.addEventListener('click', () => {
                    // Ask for confirmation in the button
                    deleteButton.innerHTML = "Confirm";
                    deleteButton.addEventListener('click', () => deleteItem(item.id,
                        pCondition));
                })
                
                sectionList.append(listItem, deleteButton);
            })
        }
    }) 
}

function deleteItem(itemId, pCondition) {
    
    // Delete an item of the list
    fetch(`/erp/api/payment_conditions/${pCondition}s/${itemId}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Couldn't delete list");
        } else {
           return response.text()
        }
    })
    .then(result => showCondition(pCondition))
}

function getCookie(name) {
    // Get cookie for CSRF token
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}