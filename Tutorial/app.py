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
