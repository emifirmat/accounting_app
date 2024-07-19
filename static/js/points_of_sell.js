document.addEventListener('DOMContentLoaded', function () {

    // Add new pos
    document.querySelector('#new-pos').addEventListener('click', () => 
        addNewPOS());
    // Show pos list
    document.querySelector('#show-pos-button').addEventListener('click', () =>
        showPOSList());
    // Disable a pos
    document.querySelectorAll('.dropdown-item.pos').forEach( function (element) {
        element.addEventListener('click', () => disablePOS());
    });

})

function addNewPOS() {
    // Add a POS through api
    event.preventDefault();
    const confirmNew = confirm('Add new POS?');
    if (confirmNew) {
        const form = document.querySelector('#new-pos-form');
        const csrftoken = getCookie('csrftoken');
        fetch(`/erp/api/points_of_sell`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pos_number: form.elements['pos_number'].value,
            }),
            mode: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Couldn't add a new POS.");
            } else {
                return response.json()
            }
        })
        .then(result => {
                messageElement = document.querySelector('#message-section')
                messageElement.innerHTML = `Point of Sell added succesfully.`;
                setTimeout(() => location.reload(), 1000);
        });
    }
}


async function showPOSList() {
    // Get and show list of POS
    const list = await getPOSList();
    
    // Clean list
    const listSection = document.querySelector('#pos-list');
    listSection.innerHTML = '';

    // Add Title
    const titleSection = document.querySelector('#show-pos-title');
    titleSection.innerHTML = 'Points of Sell';
    
    // Add item from the list
    list.forEach(item => {
        const listItem = document.createElement('li');
        listItem.innerHTML = item.pos_number;
        listSection.append(listItem);
    })
}

async function disablePOS() { 
    // Disable a POS
    const POSNumber = event.target.innerHTML.trim()
    const confirmElement = confirm(`Are you sure that you want to disable the POS number ${POSNumber}?`);
    const csrfToken = getCookie('csrftoken');
    const POSList = await getPOSList();
    let POSId;

    // get pos id
    for (let item of POSList) {
        if (item.pos_number === POSNumber) {
            POSId = item.id;
            break;
        }
    }
    if (POSId === undefined) {
        console.error('POSId not found.');
        return;
    }
    
    // If aler accepted, modify status
    if (confirmElement) {
        try {
            fetch(`/erp/api/points_of_sell/${POSId}`, {
                method: 'PATCH',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    disabled: true,
                }),
                mode: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Couldn't disable the POS.");
                } else {
                    console.log('POS disabled successfully.');
                    messageElement = document.querySelector('#message-section')
                    messageElement.innerHTML = `Point of Sell ${POSNumber} disabled.`;
                    setTimeout(() => location.reload(), 1000);
                }
            })
        } catch (error) {
            console.error('Error', error)
        }
    }
}

async function getPOSList() {
    // Get post list and pick id
    return fetch('/erp/api/points_of_sell')
    .then(response => {
        if (!response.ok) {
            throw new Error("Couldn't load the list.");
        } else {
            return response.json();
        }
    })
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