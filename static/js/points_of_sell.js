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

async function addNewPOS() {
    // Add a POS through api
    event.preventDefault();
    const confirmNew = confirm('Add new POS?');
    if (confirmNew) {
        const form = document.querySelector('#new-pos-form');
        data = {['pos_number']: form.elements['pos_number'].value};

        await postData(`/erp/api/points_of_sell`, data); // crud.js
    
        messageElement = document.querySelector('#message-section');
        messageElement.innerHTML = `Point of Sell added succesfully.`;
        setTimeout(() => location.reload(), 1000);
    };
}


async function showPOSList() {
    // Get and show list of POS
    const list = await getList('/erp/api/points_of_sell'); // crud.js
    
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
    const csrfToken = getCookie('csrftoken'); // crud.js
    const POSList = await getList('/erp/api/points_of_sell'); // crud.js
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
        const url = `/erp/api/points_of_sell/${POSId}`;
        // Disable POS
        await changeOneAttribute(url, 'disabled', true,
            'POS disabled successfully.'); // crud.js
        
        messageElement = document.querySelector('#message-section')
        messageElement.innerHTML = `Point of Sell ${POSNumber} disabled.`;
        setTimeout(() => location.reload(), 1000);
    }
}
