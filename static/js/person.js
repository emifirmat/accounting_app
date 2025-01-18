document.addEventListener('DOMContentLoaded', function() {
    // Handle edit and delete client/supplier web pages
    
    const personCRUD = document.querySelector('#person-list').dataset['personSection'];
    const filterField = document.querySelector('#filter');
    const personList = document.querySelectorAll('.specific-person');
    const personIdList = [];

    // Show, edit and delete clients or suppliers
    document.querySelectorAll('.specific-person').forEach(function (element) {
        element.addEventListener('click', async (event) => {
            const personContainer = event.target.closest('.specific-person')
            let personId = personContainer.dataset['personId'];
            const person = document.querySelector('#title').dataset.title;
            
            // Update checkbox before showing details
            if (personCRUD === 'delete') {
                const checkbox = personContainer.firstElementChild.firstElementChild;
                
                // Avoid double click in case user click on checkbox
                if (event.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                }

                updateList(checkbox, personId, personIdList);
                // Set person Id to be compatible with getPersonDetails function 
                personId = personIdList.at('-1');
       
            }
        
            const personDetails = await getPersonDetails(person, personId);

            showDetail(person, personDetails, personIdList, personCRUD);
        });
    });


    // Filter clients//supplier list
    const personArray = Array.from(personList).map(person => ({
        element: person,
        text: person.innerText.toLowerCase(),
    }));
    
    
    let timeoutId;
    filterField.addEventListener('input', () => {
        
        // Execute filter when user stop typing fast
        timeoutId = debounce(timeoutId, 200, () => 
            filterList(personArray,filterField)
        )
    
    })

});

async function showDetail(person, personDetails, personIdList, personCRUD) {
    const detailSection = document.querySelector('#detail-section');
    const detailDisplay = document.querySelector('#person-details');
    
    
    if (personCRUD === 'edit') {
        var formSection = document.querySelector('#person-edit-form');
        formSection.classList.add('hidden');
    }
    
    detailSection.classList.remove('hidden');
    detailDisplay.style.display = 'block';

    // Show details
    if (personDetails) {
        showPersonDetails(personDetails, detailDisplay);
        showButtons(person, personIdList, personDetails, detailDisplay, formSection);
    } else {
        detailDisplay.innerHTML = `<p>Select a ${person} to see details.</p>`
    }

};

async function getPersonDetails(person, personId) {
    // Get details from API
    if (personId) return await getList(`/erp/api/${person}s/${personId}`);

}

function showPersonDetails(personDetails, detailDisplay) {
    
    // Reset detailDisplay
    detailDisplay.innerHTML = '';

    // Add client or supplier details in section
    const divElement = createElementComplete({ // utils.js
        tagName: 'div',
        innerHTML:`
        <p>Number: ${personDetails.id}</p>
        <p>Name: ${personDetails.name}</p>
        <p>Address: ${personDetails.address}</p>
        <p>Email: ${personDetails.email}</p>
        <p>Phone: ${personDetails.phone}</p>
        <p>Tax Number: ${personDetails.tax_number}</p>
        `
    });

    detailDisplay.append(divElement);
}    

function showButtons(person, personIdList, personDetails, detailDisplay,
    formSection=null) {

    // Button element
    let buttonName;
    let buttonEventFunction;
    let buttonClass;

    // Handle edit button
    if (formSection) {
        buttonName = 'Edit';
        buttonClass = 'edit-button'
        buttonEventFunction = () => 
            showEditPersonForm(personDetails, detailDisplay, formSection);
    } else { // Handle delete button
        buttonClass = 'delete-button'
        if (personIdList.length < 2) {
            buttonName = 'Delete';
            buttonEventFunction = () => deletePerson(person, 
                {'personId': personDetails.id});
        } else {
            buttonName = `Delete All (${personIdList.length})`;
            buttonEventFunction = () => deletePerson(person, 
                {'personIdList': personIdList});            
        }
    }

    const buttonElement = createElementComplete({
        tagName: 'button',
        className: buttonClass,
        innerHTML: buttonName,
        eventName: 'click',
        eventFunction: buttonEventFunction
    });
    
    detailDisplay.append(buttonElement);
}

function showEditPersonForm(personDetails, detailSection, formSection) {
    // Create a prefill form for edition.
    
    detailSection.style.display = 'none';
    formSection.classList.remove('hidden');

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


async function deletePerson(person, {personId=null, personIdList=null}) {
    
    let confirmDelete;
    let url;

    // Show deleting alert
    if (personId) {
        url = `/erp/api/${person}s/${personId}`;
        confirmDelete = 
            confirm(`Are you sure that you want to delete ${person} number ${personId}?`);
    } else {
        url = `/erp/api/${person}s/bulk_delete`;
        confirmDelete = 
            confirm(`Are you sure that you want to delete ${personIdList.length} ${person}s?`);
        
    }
    if (!confirmDelete) return

    // Delete the clients/suppliers
    try {
        const deleted = await deleteInstance(url, person, personIdList); // crud.js
        
        if(!deleted) {
            let redirectUrl;
            let message;
            // Fail popup
            if (personId) {
                redirectUrl = `${personId}/related_documents`;
                message = `The ${person} couldn't be deleted because there are
                some documents linked to it. Press Accept to delete or edit them.`
                
                showPopUp('button', redirectUrl, message); // utils.js
            
            } else {
                message = `Couldn't delete the selected ${person}s because there
                are some documents linked to one or more of them.`

                showPopUp('button', '', message); // utils.js
                popupOneButton() // utils.js

            }

            return false;
        }
    
    } catch {
        // If something wrong happened, stop the function.
        console.error(`Error deleting the ${person}.`)
        return;
    }
    
    // Success popup
    let message;
    if (personId) {
        message =`The ${person} has been deleted successfully.`
    } else {
        message =`The ${person}s have been deleted successfully.`
    }  
    
    showPopUp('animation', '', message);
        
}


function filterList(personArray, filterField) {
    // Shrink the list when the filter receives user input
    const filterValue = filterField.value.toLowerCase();

    // hide clients/suppliers that doesn't include the values
    personArray.forEach(person => {
        if (person.text.includes(filterValue)) {
            person.element.classList.remove('hidden');
        } else {
            person.element.classList.add('hidden');
        }
    })

}

function updateList(checkbox, personId, personIdList) {
    // Mark/dismark checkbox and update Ids list
    
    if (!checkbox.checked) {
        // Remove selected person from the array
        const index = personIdList.indexOf(personId);
        personIdList.splice(index, 1);
    } else {
        personIdList.push(personId);
    }

}

