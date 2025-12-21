from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from app.models import db, User, Pet, Skin, UserSkin

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    skins = Skin.query.all()
    owned_skin_ids = [s.id for s in user.owned_skins]
    return render_template('shop.html', skins=skins, owned_skin_ids=owned_skin_ids, user=user)

@shop_bp.route('/buy/<int:skin_id>', methods=['POST'])
def buy_skin(skin_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    skin = db.session.get(Skin, skin_id)
    
    if not skin:
        return jsonify({'error': 'Skin not found'}), 404
    
    if skin in user.owned_skins:
        return jsonify({'error': 'Already owned'}), 400
    
    if user.coins < skin.price:
        return jsonify({'error': 'Insufficient coins'}), 400
    
    user.coins -= skin.price
    user.owned_skins.append(skin)
    db.session.commit()
    return jsonify({'success': True, 'coins': user.coins})

@shop_bp.route('/wear/<int:pet_id>/<int:skin_id>', methods=['POST'])
def wear_skin(pet_id, skin_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = db.session.get(User, session['user_id'])
    pet = db.session.get(Pet, pet_id)
    skin = db.session.get(Skin, skin_id)
    
    if not pet or pet.user_id != user.id:
        return jsonify({'error': 'Invalid pet'}), 400
    
    if skin_id != 0 and skin not in user.owned_skins:
        return jsonify({'error': 'Skin not owned'}), 400
    
    pet.current_skin_id = skin_id if skin_id != 0 else None
    db.session.commit()
    return jsonify({'success': True})
