function createElementComplete({tagName, attributeName, attributeValue, className,
    innerHTML, eventName, eventFunction}) {

    // Centralize code while creating an element
    const element = document.createElement(tagName);
    if(className) {
        element.className = className;
    }
    if(attributeName) {
        element.setAttribute(attributeName, attributeValue)
    }
    if(innerHTML) {
        element.innerHTML = innerHTML;
    }
    if(eventName) {
        element.addEventListener(eventName, eventFunction);
    }
    
    return element;
}

function showPopUp(mode, redirectUrl, content, append='false') {
    // If a person/receipt/invoice was deleted, show a pop up
    
    // element to append the popup
    const mainSection = document.querySelector('main');

    const divElement = createElementComplete({
        tagName: 'div',
        className: 'popup',
    });      

    if (append === 'true') {
        divElement.append(content);
    } else {
        divElement.innerHTML = `<span class="popup-text">${content}</span>`
    }
    
    mainSection.append(divElement);

    if(mode === 'button') {
        
        // Add a black screen to cover background
        const overlay = createElementComplete({
            tagName: 'div',
            className: 'overlay',
        });

        mainSection.append(overlay);
        
        // Use buttons
        
        divElement.style.animation = 'none';
        
        // New container for both buttons
        const newDivElement = createElementComplete({
            tagName: 'div',
            className: 'popup-footer',
        });

        divElement.append(newDivElement);

        ['Accept', 'Cancel'].forEach(element => {
            const buttonElement = createElementComplete({
                tagName: 'button',
                className: 'popup-button',
                innerHTML: element,
                eventName: 'click',
                eventFunction: () => 
                    redirectDelete(element, divElement, redirectUrl, overlay)
            });
            
            newDivElement.append(buttonElement);
        }) 

    } else if (mode === 'animation') {
        // Use animation and remove
        divElement.style.animationName = 'fadeIn';
        divElement.style.animationDuration = '3s';
        divElement.addEventListener('animationend', () => 
                window.location.href = redirectUrl
        )
    }
   
}

function redirectDelete(button, popup, redirectUrl, overlay) {
    // Redirect to invoice's related receipts.

    if(button === 'Accept') {
        window.location.href = redirectUrl;
    } else if (button === 'Cancel') {
        popup.remove();
        overlay.remove()
        return;
    }
}

function debounce(timeoutId, time, action) {
    // It debounce a function for efficiency
    
    // Restart timer
    clearTimeout(timeoutId);
    // Set timer for execution
    timeoutId = setTimeout(action, time);

    return timeoutId;
}

function popupOneButton(buttonText='Accept') {
    // Convert the popup with 2 buttons into a single button one.
    
    popupFooter = document.querySelector('.popup-footer');
    popupFooter.querySelectorAll('.popup-button')[1].textContent = buttonText;
    popupFooter.querySelectorAll('.popup-button')[0].remove();
    popupFooter.style.justifyContent = 'center';
}

function showMsgAndRestart(msg) {
    // Show a msg to the user informing the event and restarts the page

    document.querySelector('#message-section').innerHTML = msg;
    setTimeout(() => location.reload(), 1000);
}

function hideSections(...sections) {
    // Hide sections 
    
    sections.forEach(section => section.classList.add('hidden'));

}

function sortColumns(objectList, headers, column, rowType) {
    // Sort a list of rows according to a column toggling in asc and desc order

    // Get clicked column data
    const columnIndex = headers.indexOf(column);
    const columnName = column.textContent.toLowerCase();
    // Convert string data into a boolean
    const reverse = column.dataset.reverse === 'true';
    
    // Convert node into an array and sort
    const sortedList = Array.from(objectList).sort((a, b) => {
        // The list has all the rows with all the columns (w/o headers).
        // I select the cell of the column I clicked and use its text for sorting.
        const aText = a[rowType][columnIndex].textContent.trim();
        const bText = b[rowType][columnIndex].textContent.trim();
        let aValue = aText;
        let bValue = bText;
        
        // Convert currency columns to float type for accurate comparison
        if (columnName == "balance" || columnName == "total") {
            aValue = parseFloat(aText.replace("$", "").trim());
            bValue = parseFloat(bText.replace("$", "").trim());
        }

        // Convert date column to date type for accurate comparison
        if (columnName == "date") {
            aValue = convertStringToDate(aText);
            bValue = convertStringToDate(bText);
        }

        // If reverse is false, I sort in ascending order, otherwise desc.
        if (!reverse) {
            return aValue - bValue || aText.localeCompare(bText);
        } else {
            return bValue - aValue || bText.localeCompare(aText);
        }
    })

    // Toggle reverse data
    column.dataset.reverse = column.dataset.reverse === 'true' ? 'false' : 'true';

    return sortedList;

}

function convertStringToDate(dateString) {
    
    // Convert string to date
    const [day, month, year] = dateString.split('/');
    return Date.parse(`${year}-${month}-${day}`);

}