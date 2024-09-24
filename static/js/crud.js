// CRUD functions and csrf token
async function getList(url) {
    // Get list or instance
    try {
        return fetch(url)
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorMessage => {
                    throw new Error(errorMessage.detail);
                });  
            } else {
                return response.json();
            }
        })
    }
    catch(error) {
        console.error('Error', error);
    }
}

async function getSubFields(url, getResult=(result) => result) {
    // Get some attributes from an object or list of objects
    const objectOrList = await getList(url);
    return getResult(objectOrList);
}

async function postData(url, bodyData, msg="Data posted successfully.") {
    const csrftoken = getCookie('csrftoken');
    try {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bodyData),
            mode: "same-origin"
        })
        .then(response => {
            if(!response.ok) {
                return response.json().then(errorMessage => {
                    throw new Error(errorMessage.detail);
                });  
            } else {
                console.log(msg);
            }
        })
    } catch(error) {
        console.error('Error', error);
    }
}


async function changeOneAttribute(url, attributeName, attributeValue,
    msg=`The attribute '${attributeName}' was modified successfully.`) {
    // Modify the attribute of a model
    
    try {
        return fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                [attributeName]: attributeValue,
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorMessage => {
                    throw new Error(errorMessage.detail);
                });         
            } else {
                console.log(msg);
                return true;
            }
        })
    } catch (error) {
        console.error('Error' + error);
    }

}

async function deleteInstance(url, instanceName) {
    // Delete the instance of a model

    try {
        return fetch(url, {
            method: 'DELETE',
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorMessage => {
                    throw new Error(errorMessage.detail);
                });   
            } else {
                // Create pop up of confirmation
                console.log(`The ${instanceName} has been deleted successfully.`);
            }
         })
    } catch (error) {
        console.error('Error' + error);
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
