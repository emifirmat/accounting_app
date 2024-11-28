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

function showPopUp(mode, redirectUrl, content) {
    // If a person/receipt/invoice was deleted, show a pop up
    
    // element to append the popup
    const mainSection = document.querySelector('main');

    const divElement = createElementComplete({
        tagName: 'div',
        className: 'popup',
        innerHTML: `<span class="popup-text">${content}</span>`
    });      
    
    mainSection.append(divElement);

    if(mode === 'button') {
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
                    redirectDelete(element, divElement, redirectUrl)
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

function redirectDelete(button, divElement, redirectUrl) {
    // Redirect to invoice's related receipts.

    if(button === 'Accept') {
        window.location.href = redirectUrl;
    } else if (button === 'Cancel') {
        divElement.remove();
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

function popupOneButton() {
    // Convert the popup with 2 buttons into a single button one.
    
    popupFooter = document.querySelector('.popup-footer');
    popupFooter.querySelectorAll('.popup-button')[1].innerHTML = 'Accept';
    popupFooter.querySelectorAll('.popup-button')[0].remove();
    popupFooter.style.justifyContent = 'center';
}