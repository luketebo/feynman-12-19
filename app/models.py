from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    coins = db.Column(db.Integer, default=200) # 金币现在属于用户
    pets = db.relationship('Pet', backref='owner', lazy=True)
    owned_skins = db.relationship('Skin', secondary='user_skin', backref='owners')

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), default='费曼')
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    knowledge = db.Column(db.Text, default='') # 存储学到的知识，跨会话共享
    current_skin_id = db.Column(db.Integer, db.ForeignKey('skin.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship('Session', backref='pet', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    title = db.Column(db.String(100), default='新会话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='session', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Skin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))
    image_url = db.Column(db.String(200))

class UserSkin(db.Model):
    __tablename__ = 'user_skin'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skin_id = db.Column(db.Integer, db.ForeignKey('skin.id'), nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
