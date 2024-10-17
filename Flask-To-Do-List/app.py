
# pip install flask-login

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

# Flask-Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Define Task model with photo
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Link task to the logged-in user
    photo = db.Column(db.String(100))

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')

# Index route (login required)
@app.route('/')
def index():
    return render_template('index.html')

# Get tasks for the logged-in user
@app.route('/get_tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.is_completed).all()
    tasks_json = [
        {
            'id': task.id, 
            'name': task.name, 
            'is_completed': task.is_completed, 
            'photo': url_for('static', filename='uploads/' + task.photo) if task.photo else None
        } for task in tasks]
    return jsonify({'tasks': tasks_json})

# Add task (login required)
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    task_name = request.form.get('name')
    file = request.files.get('photo')
    if task_name and file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_task = Task(name=task_name, user_id=current_user.id, photo=filename)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            'task': {'id': new_task.id, 'name': new_task.name, 'is_completed': new_task.is_completed, 'photo': new_task.photo}
        })
    return jsonify({'error': 'Task name and photo are required'}), 400

# Update task (login required)
@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    task_name = request.form.get('name')
    task_is_completed = request.form.get('is_completed') == 'true'

    if task_name:
        task.name = task_name
    task.is_completed = task_is_completed
        
    db.session.commit()
    return jsonify({'task': {'id': task.id, 'name': task.name, 'is_completed': task.is_completed, 'photo': task.photo}})

# Delete task (login required)
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'result': 'Task deleted successfully'})

# Registration route (Optional)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Use the correct password hashing method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout/')
@login_required  # Ensure only logged-in users can log out
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('login'))  # Redirect to the login page

if __name__ == '__main__':
    app.run(debug=True)

