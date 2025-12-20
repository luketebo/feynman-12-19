from flask import Blueprint, render_template, redirect, url_for, session
from app.models import db, User, Message
from app.services.pet_service import get_or_create_pet

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = db.session.get(User, session['user_id'])
    pet = get_or_create_pet(user.id)
    
    messages = Message.query.filter_by(pet_id=pet.id).order_by(Message.timestamp.asc()).all()
    return render_template('index.html', user=user, pet=pet, messages=messages)
