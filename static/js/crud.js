// CRUD functions and csrf token
async function getList(url) {
    // Get list or instance
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorMessage = await response.json();
            throw new Error(errorMessage.detail || 'Unknown error.');
        } else {
            return response.json();
        }
    }
    catch(error) {
        console.error('Error: ', error.message);
        throw error;
    }
}

async function getSubFields(url, getResult=(result) => result) {
    // Get some attributes from an object or list of objects
    const objectOrList = await getList(url);
    return getResult(objectOrList);
}

async function postData(url, bodyData, msg="Data posted successfully.") {
    // Make a POST
    const csrftoken = getCookie('csrftoken');
  
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bodyData),
            mode: "same-origin"
        })
                
        if(!response.ok) {
            const errorMessage = await response.json();
            throw new Error(errorMessage.detail || "Unknown error.");
        } else {
            console.log(msg);
        }

    } catch(error) {
        console.error('Error: ', error.message);
        throw error;
    }
}

async function modifyData(url, formBody) { 
    // Modify an instance through PUT.
    const csrftoken = getCookie('csrftoken');

    // modify data  
    try {
        const response = await fetch(url, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'   
            },
            body: JSON.stringify(formBody),
            mode: 'same-origin'
        })
        
        if(!response.ok) {
            // Return error message
            return await response.json();
        } else {
            // Don't return anything and handle it in conatiner functions
            return;
        }
    } catch (error) {
        console.error('Error: ' + error);
        throw error;
    }

}

async function changeOneAttribute(url, attributeName, attributeValue,
    msg=`The attribute '${attributeName}' was modified successfully.`) {
    // Modify the attribute of a model
    
    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                [attributeName]: attributeValue,
            })
        })
        
        if (!response.ok) {
            const errorMessage = await response.json()
            throw new Error(errorMessage.detail || 'Unknown error.');
        } else {
            console.log(msg);
            return true;
        }
        
    } catch (error) {
        console.error('Error: ' + error.message);
        throw error;
    }
}

async function deleteInstance(url, instanceName) {
    // Delete the instance of a model

    try {
        const response = await fetch(url, {method: 'DELETE'})
        
        if(!response.ok) {
            if (response.status == 409) {
                // Return false so I can handle RestrictErrors in other functions.
                return false;
            } else {
                const errorMessage = await response.json();
                throw new Error(errorMessage.detail || 'Unknown error.');
            }
        } else {
            console.log(`The ${instanceName} has been deleted successfully.`);
            return true;
        }    
    } catch(error) {
        console.error('Error: ' + error.message);
        throw error;
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
