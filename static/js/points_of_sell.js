document.addEventListener('DOMContentLoaded', function () {

    // Add new pos
    document.querySelector('#new-pos').addEventListener('click', event => 
        addNewPOS(event));
    // Show pos list
    document.querySelector('#show-pos-button').addEventListener('click', () =>
        showPOSList());
    // Disable a pos
    document.querySelectorAll('.dropdown-item.pos').forEach(element => 
        element.addEventListener('click', event => disablePOS(event))
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


async function showPOSList() {
    // Get and show list of POS
    const POSlist = await getList('/erp/api/points_of_sell'); // crud.js
    
    // Clean list
    const POSlistSection = document.querySelector('#pos-list');
    POSlistSection.innerHTML = '';

    // Add Title
    const titleSection = document.querySelector('#show-pos-title');
    titleSection.innerHTML = 'Points of Sell';
    
    // Add item from the list
    POSlist.forEach(item => {
        const POSlistItem = createElementComplete({
            tagName: 'li',
            innerHTML: item.pos_number
        });
        POSlistSection.append(POSlistItem);
    })
}

async function disablePOS(event) { 
    // Disable a POS
    const POSNumber = event.target.text
    const confirmElement = confirm(
        `Are you sure that you want to disable the POS number ${POSNumber}?`
    );
    if (!confirmElement) return
    
    const POSList = await getList('/erp/api/points_of_sell'); // crud.js
    let POSId;

    // get pos id
    for (let item of POSList) {
        if (item.pos_number === POSNumber) {
            POSId = item.id;
            break;
        }
    }
    // No match
    if (POSId === undefined) {
        console.error('POSId not found.');
        return;
    }
    
    // Disable POS
    const url = `/erp/api/points_of_sell/${POSId}`;
    await changeOneAttribute(url, 'disabled', true,
        'POS disabled successfully.'); // crud.js
    
    // Show message to user
    const msg = `Point of Sell ${POSNumber} disabled.`;
    showMsgAndRestart(msg); // utils.js

}
