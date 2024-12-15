document.addEventListener("DOMContentLoaded", function() {
    
    const currentYear = document.querySelector('.dropdown-item.year.disabled');
    // Buttons and sections
    const newYearButton = document.querySelector('#add-year-tab');
    const changeYearButton = document.querySelector('#change-year-tab');
    const newYearSection = document.querySelector('#add-year-section');
    const changeYearSection = document.querySelector('#change-year-section');
    const startingSection = document.querySelector('#starting-section');

    // Change sections when user clicks
    newYearButton.addEventListener('click', () =>    
        showAndHideSections(newYearSection, [changeYearSection, startingSection])
    )
    changeYearButton.addEventListener('click', async () => {
        
        showAndHideSections(changeYearSection, [newYearSection, startingSection])
        
        // Preload years list when mouse is over the dropdown for the first time
        const dropdown = document.querySelector('#year-dropdown');
        const listUrl = "/company/api/years";
        const yearList = await loadList(listUrl, dropdown)

        // Select financial year
        document.querySelectorAll('.dropdown-item.year').forEach((element) => {
            element.addEventListener('click', async (event) => 
                setCurrentYear(event, listUrl, yearList, currentYear)
            )
        });

    })
    
});

async function loadList(listUrl, dropdownElement) {
    // Load list and update status

    const yearList = await getList(listUrl);
    dropdownElement.dataset.status = 'loaded';

    return yearList;
}


async function setCurrentYear(event, baseUrl, yearList, currentYear) {
    const newYear = event.target.innerHTML.trim();

    // Set previous current year to false
    if (currentYear != null) {
        // Search previous current year
        const oldCurrentYear = await searchCurrentYear(
            yearList, currentYear.innerHTML.trim()
        );
        
        // Change current status to false
        const oldYearUrl = baseUrl + `/${oldCurrentYear.id}`;
        await changeOneAttribute(oldYearUrl, 'current', false); // crud.js
    }
    
    // Set new current year to true
    const newCurrentYear = await searchCurrentYear(yearList, newYear);
    const newYearUrl = baseUrl + `/${newCurrentYear.id}`;

    await changeOneAttribute(newYearUrl, 'current', true); // crud.js
    
    document.querySelector('#year-dropdown').innerHTML = newCurrentYear.year;
    setTimeout(() => location.reload(), 1000);
}

async function searchCurrentYear(yearList, year) {
    // Select the one that matches year argument.
    
    // Search for a match
    for (let i = 0, len = yearList.length; i < len; i++) {
        if (yearList[i].year === year) {
            return yearList[i];
        }
    }
    
    // If for any reason there's no match
    throw new Error('No year match.');
};

function showAndHideSections(showSection, hideSections) {

    showSection.classList.remove('hidden');

    for(section of hideSections) {
        if(!section.classList.contains('hidden')) {
            section.classList.add('hidden');
        } 
    }
        
}
