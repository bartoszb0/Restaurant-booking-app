from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define DATABASE MODEL CLASS that also stands for new table with such columns
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default="user")

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    guests = db.Column(db.Integer, nullable=False)