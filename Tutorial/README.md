To create a basic CRUD (Create, Read, Update, Delete) application using Flask and AJAX, follow these steps:

### 1. **Set Up Your Flask Project**

First, install Flask if you haven't already:

```bash
pip install Flask
```

### 2. **Create the Project Structure**

Your project structure might look like this:

```
flask_ajax_crud/
│
├── app.py                # Main Flask app
├── static/
│   ├── js/
│   │   └── app.js        # AJAX logic
│   └── css/
│       └── styles.css    # Optional: Styles
├── templates/
│   └── index.html        # Frontend HTML
└── database.db           # SQLite database file (optional)
```

### 3. **Set Up Flask Application (app.py)**

Here’s a basic example of how your `app.py` could look:

```python
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Model for the item
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create the database before the first request
with app.app_context():
    db.create_all()

# Home route to render HTML
@app.route('/')
def index():
    return render_template('index.html')

# Create a new item (AJAX: POST)
@app.route('/create', methods=['POST'])
def create_item():
    name = request.json['name']
    new_item = Item(name=name)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'id': new_item.id, 'name': new_item.name})

# Read items (AJAX: GET)
@app.route('/read', methods=['GET'])
def read_items():
    items = Item.query.all()
    item_list = [{'id': item.id, 'name': item.name} for item in items]
    return jsonify(item_list)

# Update an item (AJAX: POST)
@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    item = Item.query.get(item_id)
    if item:
        item.name = request.json['name']
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    return jsonify({'message': 'Item not found'}), 404

# Delete an item (AJAX: DELETE)
@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    return jsonify({'message': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
```

### 4. **Frontend (HTML and JS)**

#### `templates/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask AJAX CRUD</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <h1>CRUD with Flask and AJAX</h1>

    <div id="item-form">
        <input type="text" id="new-item" placeholder="New item">
        <button id="create-item">Add Item</button>
    </div>

    <ul id="item-list"></ul>

    <script src="/static/js/app.js"></script>
</body>
</html>
```

#### `static/js/app.js`

```javascript
document.addEventListener('DOMContentLoaded', function () {
    const itemList = document.getElementById('item-list');
    const newItemInput = document.getElementById('new-item');
    const createItemButton = document.getElementById('create-item');

    // Fetch and display items
    function loadItems() {
        fetch('/read')
            .then(response => response.json())
            .then(data => {
                itemList.innerHTML = '';
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <input type="text" value="${item.name}" data-id="${item.id}">
                        <button class="update-item" data-id="${item.id}">Update</button>
                        <button class="delete-item" data-id="${item.id}">Delete</button>
                    `;
                    itemList.appendChild(li);
                });
            });
    }

    // Create a new item
    createItemButton.addEventListener('click', function () {
        const name = newItemInput.value;
        if (name.trim()) {
            fetch('/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            })
                .then(response => response.json())
                .then(data => {
                    newItemInput.value = '';
                    loadItems();
                });
        }
    });

    // Update an item
    itemList.addEventListener('click', function (e) {
        if (e.target.classList.contains('update-item')) {
            const id = e.target.dataset.id;
            const input = e.target.previousElementSibling;
            const name = input.value;
            fetch(`/update/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            })
                .then(response => response.json())
                .then(data => loadItems());
        }
    });

    // Delete an item
    itemList.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-item')) {
            const id = e.target.dataset.id;
            fetch(`/delete/${id}`, {
                method: 'DELETE'
            })
                .then(response => response.json())
                .then(data => loadItems());
        }
    });

    // Load items on page load
    loadItems();
});
```

### 5. **Run the Flask App**

To start the application, run:

```bash
python app.py
```

### 6. **Test the CRUD Operations**

1. **Create:** Enter a name in the input field and click "Add Item" to create a new item.
2. **Read:** All items are displayed automatically when the page loads.
3. **Update:** Change an item's name in the input field and click "Update" to modify it.
4. **Delete:** Click "Delete" next to an item to remove it.

This is a basic AJAX-powered CRUD app using Flask! You can expand it with more features like validation, error handling, or better UI.
