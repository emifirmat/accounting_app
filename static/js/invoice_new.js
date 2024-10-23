document.addEventListener('DOMContentLoaded', function() {

    // Add a new line form for invoice
    const newLineButton = document.querySelector('#new-line')
    let lineFormIndex = parseInt(
        document.querySelector('#id_s_invoice_lines-TOTAL_FORMS').value, 10) - 1;
    
    newLineButton.addEventListener('click', () => {
        // Add new line, update index and total forms
        addNewLine(lineFormIndex);
        lineFormIndex++;
        document.querySelector('#id_s_invoice_lines-TOTAL_FORMS').value = lineFormIndex;
        
    });
        
})

function addNewLine (lineFormIndex) {
    // Add a new form
    
    const formSetSection = document.querySelector('#line-form-container');
    // Copy form template
    let lineFormTemplate = document.querySelector('#line-form-template').innerHTML;
    const newLineForm = lineFormTemplate.replace(/__prefix__/g, lineFormIndex);
    
    const divElement = createElementComplete({
        tagName: 'div',
        className: 'invoice-line',
        innerHTML: `<br>${newLineForm}`
    })
    
    // Add template and update names
    formSetSection.append(divElement);

}