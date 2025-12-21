from flask import Blueprint, render_template, redirect, url_for, session
from app.models import db, User, Pet, Session, Message

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
        
    if not user.pets:
        # 如果没有宠物，创建一个默认的
        default_pet = Pet(user_id=user.id, name='费曼')
        db.session.add(default_pet)
        db.session.commit()
    
    return redirect(url_for('pet.list_pets'))

@main_bp.route('/chat/<int:session_id>')
def chat(session_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    chat_session = db.session.get(Session, session_id)
    if not chat_session or chat_session.pet.user_id != session['user_id']:
        return "Session not found", 404
    
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.asc()).all()
    return render_template('index.html', pet=chat_session.pet, chat_session=chat_session, messages=messages)
