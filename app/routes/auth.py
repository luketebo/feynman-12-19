from flask import Blueprint, render_template, redirect, url_for, session, request
from app.models import db, User
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"尝试登录/注册用户: {username}")
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.info(f"新用户注册: {username}")
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
        elif user.password != password:
            logger.warning(f"用户 {username} 登录失败: 密码错误")
            return render_template('login.html', error="密码错误，请重试")
        
        session['user_id'] = user.id
        logger.info(f"用户 {username} 登录成功 (ID: {user.id})")
        return redirect(url_for('main.index'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    logger.info(f"用户登出 (ID: {user_id})")
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
