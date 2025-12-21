from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from app.models import db, User, Pet, Session, Message
from datetime import datetime

pet_bp = Blueprint('pet', __name__, url_prefix='/pet')

@pet_bp.route('/')
def list_pets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    return render_template('pets.html', pets=user.pets)

@pet_bp.route('/create', methods=['POST'])
def create_pet():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    name = request.form.get('name', '费曼')
    new_pet = Pet(user_id=session['user_id'], name=name)
    db.session.add(new_pet)
    db.session.commit()
    return redirect(url_for('pet.list_pets'))

@pet_bp.route('/<int:pet_id>/sessions')
def list_sessions(pet_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    pet = db.session.get(Pet, pet_id)
    if not pet or pet.user_id != session['user_id']:
        return "Pet not found", 404
    return render_template('sessions.html', pet=pet, sessions=pet.sessions)

@pet_bp.route('/<int:pet_id>/sessions/create', methods=['POST'])
def create_session(pet_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    pet = db.session.get(Pet, pet_id)
    if not pet or pet.user_id != session['user_id']:
        return jsonify({'error': 'Pet not found'}), 404
    
    title = request.form.get('title', '新会话')
    new_session = Session(pet_id=pet_id, title=title)
    db.session.add(new_session)
    db.session.commit()
    return redirect(url_for('main.chat', session_id=new_session.id))
