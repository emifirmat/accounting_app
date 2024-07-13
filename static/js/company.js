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
    const newYear = event.target.innerHTML.trim()

    // Make previous current year false
    if (currentYear != null) {
        // Search previous current year
        const oldCurrentYear = await searchCurrentYear(
            currentYear.innerHTML.trim());
        
        // Change current status to false
        await changeCurrentYearStatus(oldCurrentYear, false);
    }
    
    // Make new current year true
    const newCurrentYear = await searchCurrentYear(newYear);
    await changeCurrentYearStatus(newCurrentYear, true);
    document.querySelector('#year-dropdown').innerHTML = newCurrentYear.year;
    setTimeout(() => location.reload(), 1000);
}

async function searchCurrentYear(year) {
    return fetch("/api/company/years")
    .then(response => response.json())
    .then(years => {
        // Search for a match
        for (let i = 0, len = years.length; i < len; i++) {
            if (years[i].year === year) {
                const selectedYear = years[i];
                return selectedYear;
            }
        }
        throw new Error('No year match');
    });
}

async function changeCurrentYearStatus(year, boolean) {
    const csrftoken = getCookie('csrftoken')

    return fetch('/api/company/years/' + year.id, {
        method: 'PUT',
        headers: {
            'X-CSRFToken':  csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            year: year.year,
            current: boolean
        }),
        mode: 'same-origin'
    })
    .then(response => {
        if (response.ok && boolean === true) {
            console.log('Year changed successfully.');
        }
        else if (!response.ok) {
            const errorMessage = response.json();
            throw new Error(errorMessage.detail);
        }
    })

}

function getCookie(name) {
    // Get cookie for CSRF token
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}