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

function displayTodoListsAndItems(lists) {
    // Populating the dropdown
    var activeListDropdown = document.getElementById('active-list');
    activeListDropdown.innerHTML = ''; // Clearing the dropdown

    lists.forEach(function (list) {
        var option = document.createElement('option');
        option.value = list.id;
        option.textContent = list.title;
        activeListDropdown.appendChild(option);
    });

    // Displaying the todo lists and items
    var itemsContainer = document.getElementById('items-container');
    itemsContainer.innerHTML = ''; // Clearing the container

    var activeListId = activeListDropdown.value; // Getting the selected list id

    lists.forEach(function (list) {
        if (list.id == activeListId) { // Displaying items for the selected list
            list.items.forEach(function (item) {
                var itemElement = document.createElement('div');
                itemElement.className = 'todo-item';
                itemElement.innerHTML = `
                    <p>${item.content}</p>
                    <button onclick="deleteTodo(${item.id}, true)">Delete</button>
                    <button onclick="markAsComplete(${item.id})">Complete</button>
                `;
                itemsContainer.appendChild(itemElement);
            });
        }
    });
}

function addTodoList() {
    var userId = document.body.getAttribute('data-user-id');
    console.log("user_id:", userId);  // Debug log statement
    
    var newListTitle = document.getElementById('new-list-title').value;
    sendAjaxRequest('POST', '/add-todo-list', { title: newListTitle, user_id: userId }, function (response) {
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

// Function to update a todo item
function updateTodo(id, content, isItem = true) {
    var url = isItem ? `/update-todo-item/${id}` : `/update-todo-list/${id}`;
    sendAjaxRequest('PUT', url, { content: content }, function (response) {
        fetchTodoListsAndItems();
    });
}

// Function to delete a todo item
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

// Function to create a new todo list
document.getElementById('create-list').addEventListener('click', function() {
    var title = prompt("Enter the title of the new list:");
    if (title) {
        sendAjaxRequest('POST', '/todolist', { title: title }, function(response) {
            fetchTodoListsAndItems();
        });
    }
});

// Function to edit the selected todo list
document.getElementById('edit-list').addEventListener('click', function() {
    var listId = document.getElementById('active-list').value; // Assuming the select has values as list IDs
    var newTitle = prompt("Enter the new title of the list:");
    if (newTitle) {
        sendAjaxRequest('PUT', `/update-todo-list/${listId}`, { title: newTitle }, function(response) {
            fetchTodoListsAndItems();
        });
    }
});

// Function to delete the selected todo list
document.getElementById('delete-list').addEventListener('click', function() {
    var listId = document.getElementById('active-list').value; // Assuming the select has values as list IDs
    var confirmation = confirm("Are you sure you want to delete this list?");
    if (confirmation) {
        sendAjaxRequest('DELETE', `/delete-todo-list/${listId}`, {}, function(response) {
            fetchTodoListsAndItems();
        });
    }
});

window.onload = function() {
    document.getElementById('active-list').addEventListener('change', function() {
        fetchTodoListsAndItems();
    });
};