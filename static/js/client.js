document.addEventListener('DOMContentLoaded', function() {
    // Add click event to each client
    document.querySelectorAll('.specific-client').forEach(function (element) {
        element.addEventListener('click', (event) => showDetail(event))
    });
});

async function showDetail(event) {
    const clientId = event.target.dataset['clientId'];
    const clientCRUD = document.querySelector('#client-list').dataset['clientSection'];
    let detailSection = document.querySelector('#client-details');
    if (clientCRUD === 'edit') {
        var formSection = document.querySelector('#client-edit-form');
        formSection.style.display = 'none';
    }
    
    detailSection.style.display = 'block';
    

    // Get client details
    const clientDetails = await getClientDetails(clientId);

    // Show details
    showClientDetails(clientDetails, detailSection, formSection)
};

async function getClientDetails(clientId) {
    // Get details from API
    return fetch(`/erp/api/clients/${clientId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Not response from api');
        }
        return response.json();
    })
}

function showClientDetails(clientDetails, detailSection, formSection=null) {
    // Reset detailSection
    detailSection.innerHTML = '';

    // Add client details in section
    const divElement = document.createElement('div');
    const buttonElement = document.createElement('button');
    
    // Client details
    divElement.innerHTML = `
    <p>Client number: ${clientDetails.id}</p>
    <p>Name: ${clientDetails.name}</p>
    <p>Address: ${clientDetails.address}</p>
    <p>Email: ${clientDetails.email}</p>
    <p>Phone: ${clientDetails.phone}</p>
    <p>Tax_number: ${clientDetails.tax_number}</p>
    `;
    
    // Button element
    if (formSection) {
        buttonElement.innerHTML = 'Edit';
        buttonElement.addEventListener('click', () => {
            editClientForm(clientDetails, detailSection, formSection);
        })
    } else {
        buttonElement.innerHTML = 'Delete';
        buttonElement.addEventListener('click', () => {
            deleteClient(clientDetails.id, detailSection);
        })
    }

    detailSection.append(divElement, buttonElement);
}

function editClientForm(clientDetails, detailSection, formSection) {
    detailSection.style.display = 'none';
    formSection.style.display = 'block';

    // Prefill the form
    let form = formSection.children[1];
    form.elements['name'].value = clientDetails.name;
    form.elements['address'].value = clientDetails.address;
    form.elements['email'].value = clientDetails.email;
    form.elements['phone'].value = clientDetails.phone;
    form.elements['tax_number'].value = clientDetails.tax_number;

    let submitButton = formSection.querySelector('button');
    submitButton.addEventListener('click', (event) => {
        event.preventDefault();
        confirmEdition(clientDetails.id, form);
    })
}

function confirmEdition(clientId, form) { 
    const csrftoken = getCookie('csrftoken');
    const messageElement = document.querySelector('#edit-message')

    // modify data
    fetch(`/erp/api/clients/${clientId}`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'   
        },
        body: JSON.stringify({
            name: form.elements['name'].value,
            address: form.elements['address'].value,
            email: form.elements['email'].value,
            phone: form.elements['phone'].value,
            tax_number: form.elements['tax_number'].value
        }),
        mode: 'same-origin'
    })
    .then(response => 
        response.json().then(data => ({
            status: response.status,
            ok: response.ok,
            json: data
        }))
    )    
    .then(result => {
        if (!result.ok) {
            // Wrong input, leave a message to user for fixing
            const errorMsg = result.json;
            if (errorMsg.tax_number) {
                messageElement.innerHTML = 
                    errorMsg.tax_number[0].replace('company_client', 'A client');
            } else {
                messageElement.innerHTML = `Please, check that neither of the fields
                have invalid characters.`;
            }
        } else {
            messageElement.innerHTML = `Client number ${clientId} edited 
            succesfully.`;
            setTimeout(() => location.reload(), 1000);
        }
    })
}

function deleteClient(clientId, detailSection) {
    const confirmDelete = 
        confirm(`Are you sure that you want to delete client number ${clientId}?`);

    if (confirmDelete === true) {
        fetch(`/erp/api/clients/${clientId}`, {
            method: 'DELETE'
        })
        .then(response => ({
            status: response.status,
            ok: response.ok,
        }))
        .then(result => {
            if (result.ok) {
                console.log('Client deleted successfully.');
                detailSection.style.display = 'none';
                document.querySelector('#delete-message').innerHTML = 
                    'Client deleted successfully.';
                setTimeout(() => location.reload(), 1000);
            } else {
                console.error(`Failed to delete client. ${result.json}`);
            }
        })
    }
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

