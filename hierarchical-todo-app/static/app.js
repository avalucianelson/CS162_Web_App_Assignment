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

// Function to fetch todo lists and items from the server
function fetchTodoListsAndItems() {
    sendAjaxRequest('GET', '/get-todo-lists-items', {}, function (response) {
        displayTodoListsAndItems(response.lists);
    });
}

// Function to display todo lists and items on the webpage
function displayTodoListsAndItems(lists) {
    var todoContainer = document.getElementById('todo-container');
    todoContainer.innerHTML = ''; // Clearing the container

    lists.forEach(function (list) {
        // Creating and appending list title
        var listElement = document.createElement('div');
        listElement.className = 'todo-list';
        listElement.innerHTML = `<h2>${list.title}</h2>`;
        todoContainer.appendChild(listElement);

        // Function to recursively create and append items and sub-items
        function createItems(items, parentElement) {
            items.forEach(function (item) {
                var itemElement = document.createElement('div');
                itemElement.className = 'todo-item';
                itemElement.innerHTML = `
                    <input type="text" value="${item.content}">
                    <button onclick="updateTodo(${item.id}, this.previousElementSibling.value, true)">Update</button>
                    <button onclick="deleteTodo(${item.id}, true)">Delete</button>
                    <button onclick="markAsComplete(${item.id})">Complete</button>
                `;
                parentElement.appendChild(itemElement);

                // Recursively creating and appending sub-items
                if (item.sub_items && item.sub_items.length > 0) {
                    createItems(item.sub_items, itemElement);
                }
            });
        }

        // Creating and appending items to the list
        createItems(list.items, listElement);
    });
}

// Function to add a new todo list
function addTodoList() {
    var newListTitle = document.getElementById('new-list-title').value;
    sendAjaxRequest('POST', '/add-todo-list', { title: newListTitle }, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to add a new todo item
function addTodoItem(listId, parentId = null) {
    var newItemContent = document.getElementById('new-todo').value;
    sendAjaxRequest('POST', '/add-todo-item', { content: newItemContent, list_id: listId, parent_id: parentId }, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to update a todo list or item
function updateTodo(id, content, isItem = true) {
    var url = isItem ? `/update-todo-item/${id}` : `/update-todo-list/${id}`;
    sendAjaxRequest('PUT', url, { content: content }, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to delete a todo list or item
function deleteTodo(id, isItem = true) {
    var url = isItem ? `/delete-todo-item/${id}` : `/delete-todo-list/${id}`;
    sendAjaxRequest('DELETE', url, {}, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to mark a todo item as complete
function markAsComplete(itemId) {
    sendAjaxRequest('PUT', `/mark-as-complete/${itemId}`, {}, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to move a todo item to a different list
function moveItem(itemId, newListId) {
    sendAjaxRequest('PUT', `/move-item/${itemId}`, { new_list_id: newListId }, function (response) {
        fetchTodoListsAndItems();
    });
}

// Load todo lists and items when the page loads
fetchTodoListsAndItems();
