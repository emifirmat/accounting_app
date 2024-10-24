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
    return await getList(`/erp/api/${person}s/${personId}`);
}

function showPersonDetails(personDetails, detailSection, formSection=null) {
    // Reset detailSection
    detailSection.innerHTML = '';

    // Add client or supplier details in section
    const divElement = createElementComplete({ // utils.js
        tagName: 'div',
        innerHTML:`
        <p>Number: ${personDetails.id}</p>
        <p>Name: ${personDetails.name}</p>
        <p>Address: ${personDetails.address}</p>
        <p>Email: ${personDetails.email}</p>
        <p>Phone: ${personDetails.phone}</p>
        <p>Tax_number: ${personDetails.tax_number}</p>
        `
    });
    
    // Button element
    let buttonName;
    let buttonEventFunction;

    if (formSection) {
        buttonName = 'Edit';
        buttonEventFunction = () => 
            showEditPersonForm(personDetails, detailSection, formSection);
    } else {
        buttonName = 'Delete'
        buttonEventFunction = () => deletePerson(personDetails.id, detailSection);
    }

    const buttonElement = createElementComplete({
        tagName: 'button',
        innerHTML: buttonName,
        eventName: 'click',
        eventFunction: buttonEventFunction
    });
    
    detailSection.append(divElement, buttonElement);
}

function showEditPersonForm(personDetails, detailSection, formSection) {
    // Create a prefill form for edition.
    
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

async function confirmEdition(personId, form) { 
    const messageElement = document.querySelector('#edit-message')
    let person = document.querySelector('#title').dataset.title

    // modify data
    const url = `/erp/api/${person}s/${personId}`;
    const formBody = {
            name: form.elements['name'].value,
            address: form.elements['address'].value,
            email: form.elements['email'].value,
            phone: form.elements['phone'].value,
            tax_number: form.elements['tax_number'].value
    }
    
    // Show results message
    
    const errorMessage = await modifyData(url, formBody); // crud.js
    
    if(errorMessage) {
        if(errorMessage.tax_number[0]) {
            // Tax number
            messageElement.innerHTML = errorMessage.tax_number[0]
        } else {
            // Other errors
            messageElement.innerHTML = `Please, check that neither of the fields
                have invalid characters.`;
        }
        // End function
        return
    }
    
    // Person data modified successfully
    messageElement.innerHTML = 
        `${person.charAt(0).toUpperCase() + person.slice(1)} ` +
        `number ${personId} edited succesfully.`;
    setTimeout(() => location.reload(), 1000);

}


async function deletePerson(personId, detailSection) {
    
    const person = document.querySelector('#title').dataset.title;
    const personCamel = person.charAt(0).toUpperCase() + person.slice(1);
    const confirmDelete = 
        confirm(`Are you sure that you want to delete ${person} number ${personId}?`);

    if (!confirmDelete) return

    const url = `/erp/api/${person}s/${personId}`;
    
    try {
        const deleted = await deleteInstance(url, person); // crud.js
        
        if(!deleted) {
            const redirectUrl = `${personId}/related_documents`;
            showPopUp('button', redirectUrl, // utils.js
                `The ${person} couldn't be deleted because there are some 
                documents linked to it. Press Accept to delete or edit them.`
            );
            return false;
        }
    
    } catch {
        // If something wrong happened, stop the function.
        console.error(`Error deleting the ${person}.`)
        return;
    }
    
    // element to append the popup
    showPopUp('animation', '',
        `The ${person} has been deleted successfully.`
    );
     

        
}


