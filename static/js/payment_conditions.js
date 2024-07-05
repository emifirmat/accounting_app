document.addEventListener('DOMContentLoaded', function() {
    // Add functinoality to buttoms
    document.querySelectorAll('.default-button').forEach(function (element) {
        element.addEventListener('click', () => addDefault());
    });
});

function addDefault() {
    event.preventDefault()
    
    // Add default rows to db
    const confirmDefault = confirm('Load default?');
    const pCondition = event.target.parentNode.parentNode.dataset.section;


    if (confirmDefault) {
        let data;
        if (pCondition === 'method') {
            data = [
                {'pay_method': 'Cash'}, 
                {'pay_method': 'Transfer'},
                {'pay_method': 'Check'}
            ];
        } else if (pCondition === 'term') {
            data = [
                {'pay_term': '0'}, 
                {'pay_term': '15'}, 
                {'pay_term': '30'}, 
                {'pay_term': '60'}
            ];
        } else {
            console.error('Check dataset');
            return;
        }

        // Create api point a pass it through fetch
        const csrftoken = getCookie('csrftoken');
        fetch(`/erp/api/payment_conditions/${pCondition}s`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            mode: "same-origin"
        })
        .then(response => ({
            status: response.status,
            ok: response.ok,
        }))
        .then(result => {
            if (result.ok) {
                console.log('Default loaded successfully.');
                document.querySelector('#message-section').innerHTML = `<p>Default 
                for ${pCondition} loaded successfully.</p>`;
                setTimeout(() => location.reload(), 1000);
            } else {
                console.error("Default couldn't load");
            }
        })
    }
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