document.addEventListener('DOMContentLoaded', async () => {

    // Show sections
    const newPosButton = document.querySelector('#new-tab');
    const disablePosButton = document.querySelector('#disable-tab');
    const showPosButton = document.querySelector('#show-tab');
    const newSection = document.querySelector('#new-section');
    const disableSection = document.querySelector('#disable-section');
    const showSection = document.querySelector('#show-section');
    
    // POS list is used for both show and disable functions
    let posList = await getPosList();

    newPosButton.addEventListener('click', () => {
        hideSections(disableSection, showSection);
        newSection.classList.remove('hidden');
    })
    disablePosButton.addEventListener('click', () => {
        hideSections(newSection, showSection);
        disableSection.classList.remove('hidden');
    })

    showPosButton.addEventListener('click', async () => {
        hideSections(disableSection, newSection);
        showPOSList(posList);
        showSection.classList.remove('hidden');
    })


    // Event handler for add pos button
    document.querySelector('#add-pos-button').addEventListener('click', event => 
        addNewPOS(event));
    // Event handler for Disable pos dropdown
    document.querySelectorAll('.dropdown-item.pos').forEach(element => 
        element.addEventListener('click', event => disablePOS(event, posList))
    );

})

async function addNewPOS(event) {
    // Add a POS through api
    event.preventDefault();
    const confirmNew = confirm('Add new POS?');
    
    if (!confirmNew) return
     
    // Post new pos form
    const form = document.querySelector('#new-pos-form');
    data = {['pos_number']: form.elements['pos_number'].value};
    await postData(`/erp/api/points_of_sell`, data); // crud.js

    // Show success msg to user
    const msg = `Point of Sell added succesfully.`
    showMsgAndRestart(msg); // utils.js
    
}

async function getPosList() {
    // Get and show list of POS
    try {
        return await getList('/erp/api/points_of_sell'); // crud.js
    } catch {
        console.error('There was an issue trying to get the POS list.')
    }
}


async function showPOSList(posList) {
    
    // Clean list
    const posListSection = document.querySelector('#pos-list');
    posListSection.innerHTML = '';

    // Add Title
    const titleSection = document.querySelector('#show-pos-title');
    titleSection.innerHTML = 'Points of Sell';

    // Case: empty list
    if (!posList.length) posListSection.textContent = 'No Point of Sell has been created yet.';
    
    // Add item from the list
    posList.forEach(({ pos_number, disabled }) => {
        const content = `${pos_number}`;
        
        const posListItem = createElementComplete({
            tagName: 'li',
            innerHTML: content,
            className: disabled ? 'item-disabled' : undefined
        });

        posListSection.append(posListItem);
    })
}

async function disablePOS(event, posList) { 
    // Disable a POS
    const posNumber = event.target.text
    const confirmElement = confirm(
        `Are you sure that you want to disable the POS number ${posNumber}?`
    );
    if (!confirmElement) return
    
    let posId;
    // get pos id
    for (let item of posList) {
        if (item.pos_number === posNumber) {
            posId = item.id;
            break;
        }
    }
    // No match
    if (!posId) {
        console.error('POS id not found.');
        return;
    }
    
    // Disable POS
    try {
        const url = `/erp/api/points_of_sell/${posId}`;
        await changeOneAttribute(url, 'disabled', true,
            'POS disabled successfully.'); // crud.js
    } catch {
        console.log(`There was an error trying to disable the POS ${posNumber}.`)
    }
    
    // Show message to user
    const msg = `Point of Sell ${posNumber} disabled.`;
    showMsgAndRestart(msg); // utils.js

}
