document.addEventListener("DOMContentLoaded", function() {
    // Search current year
    const currentYear = document.querySelector('.dropdown-item.year.disabled');

    // Select financial year
    document.querySelectorAll('.dropdown-item.year').forEach(function (element) {
        element.addEventListener('click', (event) => makeCurrentYear(event,
        currentYear))
    });
});


async function makeCurrentYear(event, currentYear) {
    const newYear = event.target.innerHTML.trim();
    const url = '/company/api/years/';

    // Make previous current year false
    if (currentYear != null) {
        // Search previous current year
        const oldCurrentYear = await searchCurrentYear(
            currentYear.innerHTML.trim());
        
        // Change current status to false
        const oldYearUrl = url + oldCurrentYear.id;
        await changeOneAttribute(oldYearUrl, 'current', false); // crud.js
    }
    
    // Make new current year true
    const newCurrentYear = await searchCurrentYear(newYear);
    const newYearUrl = url + newCurrentYear.id;

    await changeOneAttribute(newYearUrl, 'current', true); // crud.js
    
    document.querySelector('#year-dropdown').innerHTML = newCurrentYear.year;
    setTimeout(() => location.reload(), 1000);
}

async function searchCurrentYear(year) {
    // Search year list, and select the one that matches year argument.
    
    const yearList = await getList("/company/api/years");
    
    // Search for a match
    for (let i = 0, len = yearList.length; i < len; i++) {
        if (yearList[i].year === year) {
            return yearList[i];
        }
    }
    
    // If for any reason there's no match
    throw new Error('No year match.');
};
