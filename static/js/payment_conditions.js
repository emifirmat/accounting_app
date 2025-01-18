document.addEventListener('DOMContentLoaded', function() {
    // Add functionality to buttons

    // Buttons 
    const methodButton = document.querySelector('#method-tab');
    const termButton = document.querySelector('#term-tab');
    const defaultButton = document.querySelector('#default-tab');
    const newButton = document.querySelector('#new-tab');
    const showButton = document.querySelector('#show-tab');
    // Sections
    const welcomeSection = document.querySelector('#welcome-section');
    const termSection = document.querySelector('#term-section');
    const methodSection = document.querySelector('#method-section');
    const showSection = document.querySelector('#show-section');
    const defMethodSection = document.querySelector('#default-method');
    const newMethodSection = document.querySelector('#new-method');
    const defTermSection = document.querySelector('#default-term');
    const newTermSection = document.querySelector('#new-term');

    const secondaryNav = document.querySelector('#sec-tab-section');

    let payCondition;
    let lastClicked;
    // Active button will refresh functions while pressing method or term 
    let activeButton = [];
    
    // Navigate through buttons
    [methodButton, termButton].forEach(button =>
        button.addEventListener('click', event => {
            // Target payment conditions and show secondary buttons

            // Get information
            payCondition = event.target.dataset.condition;

            // Avoid double click
            if (lastClicked === payCondition) return;

            // Determine if default buttons should be disabled
            const emptyData = event.target.dataset.empty;
            if (emptyData === 'no') {
                defaultButton.classList.add('disabled');
            } else {
                defaultButton.classList.remove('disabled');
                prepareDefaultSection(payCondition);
            }
            // Show rest of secondary buttons
            secondaryNav.classList.remove('hidden');
            welcomeSection.classList.add('hidden');

            // Update last clicked variable
            lastClicked = payCondition;

            // Update sections when user change primary buttons
            if (activeButton.length === 0) return;

            if (activeButton[0] === 'default') {    
                toggleSections(defMethodSection, defTermSection);
            } else if (activeButton[0] === 'new') {    
                toggleSections(newMethodSection, newTermSection);
            } 
            
            
            if (activeButton[0] !== 'show') {
                activeButton[1](activeButton[0], payCondition);
            } else {
                activeButton[1](payCondition);
            }
        })

    )

    // Give action to secondary buttons
    defaultButton.addEventListener('click', () => {
  
        displaySection(
            payCondition, [methodSection, newTermSection, showSection],
            [termSection, newMethodSection, showSection], 'default'
        );

        activeButton = ['default', unhideSection];
        
    });
    newButton.addEventListener('click', () => {

        displaySection(
            payCondition, [methodSection, defTermSection, showSection],
            [termSection, defMethodSection, showSection], 'new'
        ); 

        activeButton = ['new', unhideSection];

    });
    showButton.addEventListener('click', () => {

        hideSections(termSection, methodSection); // utils.py
        showCondition(payCondition);

        // Remove hidding attribute
        showSection.classList.remove('hidden');

        activeButton = ['show', showCondition];

    });

    // Add event to new term and new method buttons in advance
    const newMethodButton = newMethodSection.querySelector('button');
    const newTermButton = newTermSection.querySelector('button');

    [newMethodButton, newTermButton].forEach(button => 
        button.addEventListener('click', async event => {
        
            event.preventDefault();
            const confirmNew = confirm(`Add new ${payCondition}?`);
            if (!confirmNew) return;
            
            await insertNewPCondition(payCondition);
    
        })
    )

});


function toggleSections(section1, section2) {
    // Toggle sections 1 and 2 

    [section1, section2].forEach(section => section.classList.toggle('hidden'))

}


function displaySection(pCondition, hideIfTerm, hideIfMethod, category) {
    // Hide some sections and show others
    
    if (pCondition === 'term') {
        hideSections(...hideIfTerm); // utils.py
    } else if (pCondition === 'method') {
        hideSections(...hideIfMethod); // utils.py
    }

    unhideSection(category, pCondition);

}

function prepareDefaultSection(pCondition) {
    // Add event to default term and default method buttons in advance
    const defSection = document.querySelector(`#default-${pCondition}`);
    const defLoadButton = defSection.querySelector('button');
    
    // Add loaded status to run click load event once.
    if (defSection.dataset.loaded === 'true') return
    defSection.dataset.loaded = 'true';

    // Add event to load section
    defLoadButton.addEventListener('click', async event => {
        
            event.preventDefault();
            
            // Add event to load button
            data = loadDefaultData(pCondition);
            await postDefaultData(pCondition, data);
    
        })
    
    }

function loadDefaultData(pCondition) {
    // Set and return default data
    
    let data;
    if (pCondition === 'method') {
        data = [
            {'pay_method': 'Cash'}, 
            {'pay_method': 'Transfer'},
            {'pay_method': 'Check'}
        ];
        dataText = data.map(item => item.pay_method);
    } else if (pCondition === 'term') {
        data = [
            {'pay_term': '0'}, 
            {'pay_term': '15'}, 
            {'pay_term': '30'}, 
            {'pay_term': '60'}
        ];
        dataText = data.map(item => item.pay_term);
    }

    return data;

}
    
async function postDefaultData(pCondition, data) {
    // Take data as an argument and post it through api point.
    
    // Show alert   
    const confirmDefault = confirm('Load default values?');
    if (!confirmDefault) return;

    // Add default payments or terms to db
    const successMsg = `Default ${pCondition}s loaded successfully.`;
    const url = `/erp/api/payment_conditions/${pCondition}s`;
    
    try {  
        await postData(url, data, successMsg); // crud.js
    } catch {
        console.error(`Error adding default ${pCondition}s`);
        return;
    }
    
    // Show success message
    showPopUp('animation', '', successMsg);
    
}

function unhideSection(category, pCondition) {
    // Show the default section

    const sectionDiv = document.querySelector(`#${category}-${pCondition}`);
    sectionDiv.classList.remove('hidden');
    sectionDiv.parentElement.classList.remove('hidden');

}

async function showCondition(pCondition) {
    
    // Get list through fetch
    const url = `/erp/api/payment_conditions/${pCondition}s`;
    const sectionTitle = document.querySelector('#show-title');
    const sectionList = document.querySelector('#show-list');
    sectionList.innerHTML = '';
    try {
        const pConditionList = await getList(url); // crud.js
  
        // Show a message if there aren't any values
        if (!pConditionList.length) {
            sectionList.textContent = `You haven't added any ${pCondition} yet.`;
        } else {
            // Add title
            sectionTitle.textContent = `Payment ${pCondition}s`;
            // Add all methods/terms of the list
            addShowSectionContent(pCondition, pConditionList, sectionList);
        }
    } catch {
        console.error(`Couldn't retrieve the payment ${pCondition} list. Please,
        contact the admin.`);
        sectionList.textContent = `An error occurred while loading the ${pCondition}
        list. Please try again later.`;
    }
   
}

function addShowSectionContent(pCondition, pConditionList, sectionList) {
    // Add pConditionList with delete buttons in show section

    pConditionList.forEach(item => {
        const divElement = createElementComplete({
            tagName: 'div',
            className: 'row numbered-item'
        })
        
        // Customize item
        let property;
        if (pCondition === "method") {
            property = 'pay_method';
        } else if (pCondition === "term") {
            property = 'pay_term';
        }
        divElement.innerHTML = `<div class="col-8">${item[property]}</div>`;

        // Customize delete button
        const deleteButton = createElementComplete({
            tagName: 'button',
            className: 'delete-item col-4',
            innerHTML: 'Delete',
            eventName: 'click',
            eventFunction: () => {
                // Ask for confirmation in the button
                deleteButton.innerHTML = "Confirm";
                deleteButton.addEventListener('click', () => deleteItem(
                    item.id, pCondition));
            }
        });
        
        divElement.append(deleteButton);
        sectionList.append(divElement);
    })

}

async function deleteItem(itemId, pCondition) {
    
    // Delete an item of the list
    const url = `/erp/api/payment_conditions/${pCondition}s/${itemId}`;
    try {
        const deleted = await deleteInstance(url, pCondition); // crud.js
        
        // Restricted error
        if (!deleted) {
            showPopUp('button', '', `There are invoices using this ${pCondition}.
            To proceed, you'll have to manually delete them.`); // utils.js
            // Alter popup style
            popupOneButton(); // utils.js
            return false; 
        }

        // Restart view section
        showCondition(pCondition);
        
    } catch {
        // If something wrong happened, stop the function.
        console.error(`Error deleting the ${pCondition}s.`)
    } 
}

async function insertNewPCondition(pCondition) {
    // Add new entry to db

    // Set data to post 
    const newSection = document.querySelector(`#new-${pCondition}`)
    const form = newSection.children[0];
    const data = {[`pay_${pCondition}`]: form.elements[`pay_${pCondition}`].value};

    // Pass data through fetch
    const url = `/erp/api/payment_conditions/${pCondition}s`;
    try {
        await postData(url, data, `New ${pCondition} added successfully.`); // crud.js
    } catch {
        console.error(`An error ocurred while inserting a new ${pCondition}.`)
    }
    
    // Success pop up
    showPopUp('animation', '', `New ${pCondition} added successfully.`);
    
}