from flask import Blueprint, request, jsonify, session, Response, current_app
from app.models import db, User, Message, Session, Pet
from app.services.ai_service import stream_feynman_response
from app.services.pet_service import update_pet_growth
import json
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_bp.route('/chat_stream', methods=['POST'])
def chat_stream():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    session_id = request.json.get('session_id')
    chat_session = db.session.get(Session, session_id)
    
    if not chat_session or chat_session.pet.user_id != session['user_id']:
        logger.warning(f"非法会话访问: session_id={session_id}, user_id={session.get('user_id')}")
        return jsonify({'error': 'Invalid session'}), 400
        
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400

    logger.info(f"收到用户消息 (Session: {session_id}): {user_input[:50]}...")

    # 保存用户消息
    user_msg = Message(session_id=session_id, role='user', content=user_input)
    db.session.add(user_msg)
    db.session.commit()
    
    # 获取历史对话
    history = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.desc()).limit(10).all()
    history_msgs = [{"role": m.role, "content": m.content} for m in reversed(history)]

    # 获取宠物信息和知识
    pet = chat_session.pet
    pet_name = pet.name
    pet_knowledge = pet.knowledge

    # 获取真实的 app 对象以在生成器中使用
    app = current_app._get_current_object()
    pet_id = pet.id

    def generate():
        full_content = ""
        logger.debug(f"开始调用 AI 服务 (Pet: {pet_name})")
        for chunk in stream_feynman_response(history_msgs, pet_name=pet_name, pet_knowledge=pet_knowledge):
            full_content += chunk
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        
        logger.debug(f"AI 回复完成，长度: {len(full_content)}")
        
        with app.app_context():
            current_pet = db.session.get(Pet, pet_id)
            ai_msg = Message(session_id=session_id, role='assistant', content=full_content)
            db.session.add(ai_msg)
            
            # 更新成长和知识
            logger.debug(f"正在更新宠物成长状态 (Pet ID: {pet_id})")
            update_pet_growth(current_pet, full_content, history_msgs + [{"role": "assistant", "content": full_content}])
            db.session.commit()
            
            final_status = {
                'level': current_pet.level,
                'experience': current_pet.experience,
                'coins': current_pet.owner.coins,
                'knowledge': current_pet.knowledge,
                'done': True
            }
            logger.info(f"会话状态更新完成: Level={current_pet.level}, Coins={current_pet.owner.coins}")
            yield f"data: {json.dumps(final_status, ensure_ascii=False)}\n\n"

    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    return response
