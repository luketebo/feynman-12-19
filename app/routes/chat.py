from flask import Blueprint, request, jsonify, session, Response, current_app
from app.models import db, User, Message
from app.services.ai_service import stream_feynman_response
from app.services.pet_service import update_pet_growth
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat_stream', methods=['POST'])
def chat_stream():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = db.session.get(User, session['user_id'])
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    # 保存用户消息
    user_msg = Message(pet_id=user.pet.id, role='user', content=user_input)
    db.session.add(user_msg)
    db.session.commit()
    
    # 获取历史对话
    history = Message.query.filter_by(pet_id=user.pet.id).order_by(Message.timestamp.desc()).limit(10).all()
    history_msgs = [{"role": m.role, "content": m.content} for m in reversed(history)]

    # 获取真实的 app 对象以在生成器中使用
    app = current_app._get_current_object()
    user_id = user.id

    def generate():
        full_content = ""
        for chunk in stream_feynman_response(history_msgs):
            full_content += chunk
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        
        with app.app_context():
            current_user = db.session.get(User, user_id)
            ai_msg = Message(pet_id=current_user.pet.id, role='assistant', content=full_content)
            db.session.add(ai_msg)
            
            update_pet_growth(current_user.pet, full_content)
            db.session.commit()
            
            final_status = {
                'level': current_user.pet.level,
                'experience': current_user.pet.experience,
                'coins': current_user.pet.coins,
                'done': True
            }
            yield f"data: {json.dumps(final_status, ensure_ascii=False)}\n\n"

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response
