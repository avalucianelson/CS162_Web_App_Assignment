// Function to send AJAX requests
function sendAjaxRequest(method, url, data, successCallback) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            successCallback(JSON.parse(xhr.responseText));
        }
    };
    xhr.send(JSON.stringify(data));
}

// Function to fetch todo items from the server
function fetchTodoItems() {
    // Sending a GET request to the server to retrieve todo items
    sendAjaxRequest('GET', '/get-todo-items', {}, function (response) {
        // Displaying the fetched todo items on the webpage
        displayTodoItems(response.items);
    });
}

// Function to display todo items on the webpage
function displayTodoItems(items) {
    var todoListContainer = document.getElementById('todo-list-container');
    todoListContainer.innerHTML = ''; // Clearing the container

    items.forEach(function (item) {
        var itemElement = document.createElement('div');
        itemElement.innerText = item.content;
        todoListContainer.appendChild(itemElement);
    });
}

// Function to add a new todo item
function addTodoItem() {
    var newItemContent = document.getElementById('new-item-content').value;

    // Sending a POST request to the server to add a new todo item
    sendAjaxRequest('POST', '/add-todo-item', { content: newItemContent }, function (response) {
        // Fetching and displaying the updated list of todo items
        fetchTodoItems();
    });
}

// Function to complete a todo item
function completeTodoItem(itemId) {
    // Sending a PUT request to the server to mark a todo item as completed
    sendAjaxRequest('PUT', '/complete-todo-item/' + itemId, {}, function (response) {
        // Fetching and displaying the updated list of todo items
        fetchTodoItems();
    });
}

// Function to delete a todo item
function deleteTodoItem(itemId) {
    // Sending a DELETE request to the server to delete a todo item
    sendAjaxRequest('DELETE', '/delete-todo-item/' + itemId, {}, function (response) {
        // Fetching and displaying the updated list of todo items
        fetchTodoItems();
    });
}

// Load todo items when the page loads
fetchTodoItems();