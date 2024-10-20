from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect users to the login page if not logged in

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

# Item model, related to the User
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database before the first request
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route to render HTML
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Register new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        # Add new user to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully.')
        return redirect(url_for('login'))
    return render_template('register.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')

# User logout
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Create a new item (AJAX: POST)
@app.route('/create', methods=['POST'])
@login_required
def create_item():
    name = request.json['name']
    new_item = Item(name=name, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'id': new_item.id, 'name': new_item.name})

# Read items (AJAX: GET)
@app.route('/read', methods=['GET'])
@login_required
def read_items():
    items = Item.query.filter_by(user_id=current_user.id).all()
    item_list = [{'id': item.id, 'name': item.name} for item in items]
    return jsonify(item_list)

# Update an item (AJAX: POST)
@app.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        item.name = request.json['name']
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    return jsonify({'message': 'Item not found'}), 404

# Delete an item (AJAX: DELETE)
@app.route('/delete/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    return jsonify({'message': 'Item not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
