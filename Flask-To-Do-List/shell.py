from app import db, app

# Use app context to ensure database operations work properly
with app.app_context():
    db.create_all()
