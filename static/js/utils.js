function createElementComplete({tagName, className, innerHTML, eventName, 
    eventFunction}) {

    // Centralize code while creating an element
    const element = document.createElement(tagName);
    if(className) {
        element.className = className;
    }
    if(innerHTML) {
        element.innerHTML = innerHTML;
    }
    if(eventName) {
        element.addEventListener(eventName, eventFunction);
    }
    
    return element;
}