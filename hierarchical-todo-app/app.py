from flask import Flask, request, session, jsonify, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Initializing the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'I_dont_really_care_if_this_is_secure' # adding a secret key

# Configuring the database URI for SQLAlchemy
# Using SQLite for simplicity, creating a file 'site.db' in the project directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)  # Initializing the database with the app configuration
migrate = Migrate(app, db)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each user
    username = db.Column(db.String(50), unique=True, nullable=False)  # Username, must be unique and not null
    password = db.Column(db.String(60), nullable=False)  # Password, hashed, not null
    lists = db.relationship('TodoList', backref='user', lazy=True)  # Relationship with TodoList, one user to many lists


# TodoList Model
class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each list
    title = db.Column(db.String(100), nullable=False)  # Title of the todo list, not null
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key referencing User model
    items = db.relationship('TodoItem', backref='list', lazy=True)  # Relationship with TodoItem, one list to many items


# TodoItem Model
class TodoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key, unique identifier for each item
    content = db.Column(db.String(200), nullable=False)  # Content of the todo item, not null
    list_id = db.Column(db.Integer, db.ForeignKey('todo_list.id'), nullable=False)  # Foreign key referencing TodoList model 
    # Self-referencing foreign key to implement hierarchical todo items (sub-items)
    parent_id = db.Column(db.Integer, db.ForeignKey('todo_item.id'), nullable=True)  
    # Relationship for handling sub-items. Each item can have multiple sub-items.
    sub_items = db.relationship('TodoItem', backref=db.backref('parent', remote_side=[id]), lazy=True)  
    completed = db.Column(db.Boolean, default=False)  # Boolean to track whether a todo item is completed or not


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if the request method is POST, meaning the form has been submitted
    if request.method == 'POST':
        # Retrieve the username and password from the form data
        username = request.form['username']
        password = request.form['password']  # Get the password 
        
        # Check if a user with the submitted username already exists in the database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # If the username exists, flash an error message and redirect to the registration page
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))
        else:
            # If the username doesn't exist, create a new user and add it to the database
            new_user = User(username=username, password=password)  # Store the password
            db.session.add(new_user)
            db.session.commit()

        # Flash a success message and redirect to the login page
        flash('User registered successfully. You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirecting to the login page after successful registration

    # If the request method is GET, render the registration page
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id  # Store user_id in the session
            flash('Login successful. Welcome back!', 'success')
            return redirect(url_for('todo'))  # Redirecting to the todo page after successful login
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')



# Route for creating todo lists
@app.route('/todolist', methods=['POST'])
def create_todolist():
    data = request.get_json()  # Getting the JSON data from the request
    title = data.get('title')  # Extracting the title of the todo list from the data
    # user_id = data.get('user_id')  # Extracting the user_id from the data
    user_id = session['user_id']
    print(user_id)

    # Creating a new TodoList object with the provided title and user_id
    new_list = TodoList(title=title, user_id=user_id)
    db.session.add(new_list)  # Adding the new todo list to the database session
    db.session.commit()  # Committing the session to save the todo list in the database

    return jsonify({"message": "Todo list created successfully."}), 201  # Returning a success message


@app.route('/update-todo-list/<int:list_id>', methods=['PUT'])
def update_todo_list(list_id):
    data = request.get_json()
    title = data.get('title')

    todo_list = TodoList.query.get(list_id)
    if todo_list:
        todo_list.title = title
        db.session.commit()
        return jsonify({"message": "Todo list updated successfully."}), 200
    else:
        return jsonify({"message": "Todo list not found."}), 404


@app.route('/update-todo-item/<int:item_id>', methods=['PUT'])
def update_todoitem(item_id):
    data = request.get_json()
    todo_item = TodoItem.query.get(item_id)
    
    if todo_item:
        todo_item.content = data.get('content', todo_item.content)
        todo_item.completed = data.get('completed', todo_item.completed)
        db.session.commit()
        return jsonify({"message": "Todo item updated successfully."}), 200
    else:
        return jsonify({"message": "Todo item not found."}), 404


# Route for adding items to the todo lists
@app.route('/todoitem', methods=['POST'])
def create_todoitem():
    data = request.get_json()  # Getting the JSON data from the request
    content = data.get('content')  # Extracting the content of the todo item from the data
    list_id = data.get('list_id')  # Extracting the list_id from the data

    # Creating a new TodoItem object with the provided content and list_id
    new_item = TodoItem(content=content, list_id=list_id)
    db.session.add(new_item)  # Adding the new todo item to the database session
    db.session.commit()  # Committing the session to save the todo item in the database

    return jsonify({"message": "Todo item added successfully."}), 201  # Returning a success message


@app.route('/todoitem/<int:item_id>/complete', methods=['PUT'])
def complete_todoitem(item_id):
    todo_item = TodoItem.query.get(item_id)  # Querying the database to find the todo item by its ID

    if todo_item:  # Checking if the todo item exists
        todo_item.completed = True  # Marking the todo item as complete
        db.session.commit()  # Committing the changes to the database
        return jsonify({"message": f"Todo item {item_id} marked as complete."}), 200  # Returning a success message
    else:
        return jsonify({"message": "Todo item not found."}), 404  # Returning a message if the todo item does not exist


def mark_as_complete(item_id):
    """
    Mark a todo item as complete.
    :param item_id: ID of the todo item to be marked as complete.
    """
    # Querying the database to find the todo item by its ID
    todo_item = TodoItem.query.get(item_id)

    if todo_item:  # Checking if the todo item exists
        # Logic to mark the todo item as complete can be added here
        # For example, you might want to add a 'completed' column to your TodoItem model
        # todo_item.completed = True  # Assuming you have a 'completed' column

        db.session.commit()  # Committing the changes to the database

        return jsonify({"message": f"Todo item {item_id} marked as complete."}), 200  # Returning a success message
    else:
        return jsonify({"message": "Todo item not found."}), 404  # Returning a message if the todo item does not exist


@app.route('/delete-todo-list/<int:list_id>', methods=['DELETE'])
def delete_todo_list(list_id):
    todo_list = TodoList.query.get(list_id)
    if todo_list:
        db.session.delete(todo_list)
        db.session.commit()
        return jsonify({"message": "Todo list deleted successfully."}), 200
    else:
        return jsonify({"message": "Todo list not found."}), 404


# Route for deleting a todo item
@app.route('/delete-todo-item/<int:item_id>', methods=['DELETE'])
def delete_todoitem(item_id):
    """
    Delete a todo item by its ID.
    :param item_id: ID of the todo item to be deleted.
    """

    # Querying the database to find the todo item by its ID
    todo_item = TodoItem.query.get(item_id)

    if todo_item:  # Checking if the todo item exists
        db.session.delete(todo_item)  # Deleting the todo item from the database session
        db.session.commit()  # Committing the changes to the database

        return jsonify({"message": f"Todo item {item_id} deleted successfully."}), 200  # Returning a success message

    else:
        return jsonify({"message": "Todo item not found."}), 404  # Returning a message if the todo item does not exist


@app.route('/add-todo-list', methods=['POST'])
def add_todo_list():
    print("This workssssss")
    
    return jsonify({"message": "Todo list added successfully."}), 201



@app.route('/add-todo-item', methods=['POST'])
def add_todo_item():
    data = request.get_json()
    content = data.get('content')
    list_id = data.get('list_id')
    parent_id = data.get('parent_id', None)

    new_item = TodoItem(content=content, list_id=list_id, parent_id=parent_id)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Todo item added successfully."}), 201


@app.route('/get-todo-lists-items', methods=['GET'])
def get_todo_lists_items():
    lists = TodoList.query.all()
    lists_data = []

    for list in lists:
        list_items = []
        for item in list.items:
            if not item.parent_id:  # Only top-level items
                list_items.append({
                    'id': item.id,
                    'content': item.content,
                    'completed': item.completed,
                    'sub_items': get_sub_items(item.sub_items)  # Recursive function to get sub-items
                })
        lists_data.append({
            'id': list.id,
            'title': list.title,
            'items': list_items
        })

    return jsonify(lists_data)


def get_sub_items(sub_items):
    items = []
    for item in sub_items:
        items.append({
            'id': item.id,
            'content': item.content,
            'completed': item.completed,
            'sub_items': get_sub_items(item.sub_items)
        })
    return items


@app.route('/get-todo-items', methods=['GET'])
def get_todo_items():
    # Querying all todo lists and their items from the database
    todo_lists = TodoList.query.all()

    # Creating a list to hold the todo lists and their items
    lists_data = []

    for todo_list in todo_lists:
        # Creating a dictionary to hold each todo list and its items
        list_data = {
            'id': todo_list.id,
            'title': todo_list.title,
            'items': []
        }

        # Adding each item in the current todo list to the list_data dictionary
        for item in todo_list.items:
            item_data = {
                'id': item.id,
                'content': item.content,
                'completed': item.completed
            }
            list_data['items'].append(item_data)

        # Adding the list_data dictionary to the lists_data list
        lists_data.append(list_data)

    # Returning the lists_data as JSON
    return jsonify(lists_data)


@app.route('/move-item/<int:item_id>', methods=['PUT'])
def move_item(item_id):
    data = request.get_json()
    new_list_id = data.get('new_list_id')

    todo_item = TodoItem.query.get(item_id)
    if todo_item:
        todo_item.list_id = new_list_id
        db.session.commit()
        return jsonify({"message": "Todo item moved successfully."}), 200
    else:
        return jsonify({"message": "Todo item not found."}), 404



@app.route('/todo')
def todo():
    user_id = session.get('user_id')  # Get user_id from the session
    if user_id:  # Check if user_id exists in the session
        return render_template('todo.html', user_id=user_id)  # Pass user_id to the template
    else:
        flash('Please login to access the todo page.', 'danger')
        return redirect(url_for('login'))  # Redirect to login if no user_id in session


@app.route('/')
def home():
    return render_template('index.html')  # the home page


# Main block to run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the database and tables, it runs only when the script is executed directly

    app.run(debug=True)  # Running the Flask application in debug mode
