document.addEventListener('DOMContentLoaded', function() {
    // Add click event to each client or supplier
    document.querySelectorAll('.specific-person').forEach(function (element) {
        element.addEventListener('click', (event) => showDetail(event));
    });
});

async function showDetail(event) {
    const personId = event.target.dataset['personId'];
    const personCRUD = document.querySelector('#person-list').dataset['personSection'];
    let detailSection = document.querySelector('#person-details');
    if (personCRUD === 'edit') {
        var formSection = document.querySelector('#person-edit-form');
        formSection.style.display = 'none';
    }
    
    detailSection.style.display = 'block';

    // Get client or supplier details
    const personDetails = await getPersonDetails(personId);

    // Show details
    showPersonDetails(personDetails, detailSection, formSection);
};

async function getPersonDetails(personId) {
    // Get details from API
    const person = document.querySelector('#title').dataset.title;
    return getList(`/erp/api/${person}s/${personId}`);
}

function showPersonDetails(personDetails, detailSection, formSection=null) {
    // Reset detailSection
    detailSection.innerHTML = '';

    // Add client or supplier details in section
    const divElement = document.createElement('div');
    const buttonElement = document.createElement('button');
    
    // Client or supplier details
    divElement.innerHTML = `
    <p>Number: ${personDetails.id}</p>
    <p>Name: ${personDetails.name}</p>
    <p>Address: ${personDetails.address}</p>
    <p>Email: ${personDetails.email}</p>
    <p>Phone: ${personDetails.phone}</p>
    <p>Tax_number: ${personDetails.tax_number}</p>
    `;
    
    // Button element
    if (formSection) {
        buttonElement.innerHTML = 'Edit';
        buttonElement.addEventListener('click', () => {
            editPersonForm(personDetails, detailSection, formSection);
        })
    } else {
        buttonElement.innerHTML = 'Delete';
        buttonElement.addEventListener('click', () => {
            deletePerson(personDetails.id, detailSection);
        })
    }

    detailSection.append(divElement, buttonElement);
}

function editPersonForm(personDetails, detailSection, formSection) {
    detailSection.style.display = 'none';
    formSection.style.display = 'block';

    // Prefill the form
    let form = formSection.children[1];
    form.elements['name'].value = personDetails.name;
    form.elements['address'].value = personDetails.address;
    form.elements['email'].value = personDetails.email;
    form.elements['phone'].value = personDetails.phone;
    form.elements['tax_number'].value = personDetails.tax_number;

    let submitButton = formSection.querySelector('button');
    submitButton.addEventListener('click', (event) => {
        event.preventDefault();
        confirmEdition(personDetails.id, form);
    })
}

function confirmEdition(personId, form) { 
    const csrftoken = getCookie('csrftoken');
    const messageElement = document.querySelector('#edit-message')
    let person = document.querySelector('#title').dataset.title

    // modify data
    const url = `/erp/api/${person}s/${personId}`;
    fetch(`/erp/api/${person}s/${personId}`, {
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
            messageElement.innerHTML = `${person.charAt(0).toUpperCase() + person.slice(1)}
            number ${personId} edited succesfully.`;
            setTimeout(() => location.reload(), 1000);
        }
    })
}

async function deletePerson(personId, detailSection) {
    const person = document.querySelector('#title').dataset.title;
    const personCamel = person.charAt(0).toUpperCase() + person.slice(1);
    const confirmDelete = 
        confirm(`Are you sure that you want to delete ${person} number ${personId}?`);

    if (confirmDelete === true) {
        const url = `/erp/api/${person}s/${personId}`;
        await deleteInstance(url, {person}); // crud.js
        
        detailSection.style.display = 'none';
        document.querySelector('#delete-message').innerHTML = 
            `${personCamel} deleted successfully.`;
        setTimeout(() => location.reload(), 1000);

    }
}


