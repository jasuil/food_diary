from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

# create the extension
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    user_name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=False)
    pw = db.Column(db.String(1000), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)

class UserSession(db.Model):
    user_id = db.Column(db.String(100), primary_key=True, nullable=False)
    cookie_value = db.Column(db.String(1000), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)
    expire_at = db.Column(db.DateTime, nullable=False)

class DailyDish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime, nullable=False)

class DailyDishDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_dish_id = db.Column(db.Integer, ForeignKey("daily_dish.id"))
    dishes = db.Column(db.String(1000), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)
