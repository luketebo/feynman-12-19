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
    
    # 2. 通过会话找到对应的宠物对象
    # 因为你在 Session 模型里定义了 backref='pet'，所以可以直接用
    my_pet_object = chat_session.pet

    # --- 关键点来了 ---
    # 此时，my_pet_object.current_skin 就已经是那个皮肤对象了（如果它有皮肤的话）
    # 我们可以先准备好图片 URL，处理一下它没有皮肤的默认情况
    
    # 默认头像（假设在 static/img/default_avatar.png）
    avatar_filename = 'img/doujun_normal.png' 
    
    if my_pet_object.current_skin: 
        avatar_filename = 'img/' + my_pet_object.current_skin.image_url
    
    messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.asc()).all()
    return render_template('index.html', pet=chat_session.pet, chat_session=chat_session, messages=messages,avatar_filename=avatar_filename)
