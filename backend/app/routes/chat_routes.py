from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat import ChatSession, ChatMessage
from app.services.chat_service import ChatService
from app import db

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    user_id = get_jwt_identity()
    new_session = ChatSession(user_id=user_id, title="Новый разбор партии")
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"session_id": new_session.id, "title": new_session.title}), 201

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    user_id = get_jwt_identity()
    sessions = ChatSession.query.filter_by(user_id=user_id).order_by(ChatSession.created_at.desc()).all()
    return jsonify([{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in sessions])

@chat_bp.route('/sessions/<int:session_id>/send', methods=['POST'])
@jwt_required()
def send_message(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.get_or_404(session_id)
    
    if session.user_id != int(user_id):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    user_text = data.get('message')
    if not user_text:
        return jsonify({"error": "Message is required"}), 400

    user_msg = ChatMessage(session_id=session_id, role='user', content=user_text)
    db.session.add(user_msg)

    ai_response_text = ChatService.get_ai_response(user_id, user_text)

    assistant_msg = ChatMessage(session_id=session_id, role='assistant', content=ai_response_text)
    db.session.add(assistant_msg)
    
    db.session.commit()

    return jsonify({
        "user_message": user_text,
        "assistant_response": ai_response_text
    })

@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
def get_session_messages(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.get_or_404(session_id)
    
    if session.user_id != int(user_id):
        return jsonify({"error": "Access denied"}), 403

    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
    
    return jsonify([
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        } for m in messages
    ])

@chat_bp.route('/sessions/<int:session_id>/messages', methods=['GET', 'POST'])
@jwt_required()
def handle_messages(session_id):
    user_id = get_jwt_identity()
    session = ChatSession.query.get_or_404(session_id)
    
    if session.user_id != int(user_id):
        return jsonify({"error": "Forbidden"}), 403

    if request.method == 'GET':
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
        result = []
        for m in messages:
            result.append({
                'id': m.id,
                'role': m.role,
                'content': m.content,
                'created_at': m.created_at.isoformat()
            })
        return jsonify(result), 200

    if request.method == 'POST':
        data = request.get_json()
        user_text = data.get('message')
        
        if not user_text:
            return jsonify({"error": "Message is required"}), 400

        user_msg = ChatMessage(session_id=session_id, role='user', content=user_text)
        db.session.add(user_msg)
        
        ai_response = ChatService.get_ai_response(user_id, user_text)
        
        assistant_msg = ChatMessage(session_id=session_id, role='assistant', content=ai_response)
        db.session.add(assistant_msg)
        
        db.session.commit()
        
        return jsonify({
            "id": assistant_msg.id,
            "role": "assistant",
            "content": ai_response,
            "created_at": assistant_msg.created_at.isoformat()
        }), 201