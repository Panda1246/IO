from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user
from sqlalchemy import or_

from app.extensions import db
from app.models.message import Message
from app.models.user import User

bp = Blueprint('chat', __name__,
               template_folder='../templates/communication',
               static_folder='static',
               static_url_path='communication')


@bp.route('/')
def index():
    users = User.query.all()
    return render_template('communication/chat.html', users=users)


@bp.route('/chat')
def chat():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(id=current_user.id).first()
    if not user:
        return redirect(url_for('index'))

    # Znajdź wszystkich użytkowników, z którymi dany użytkownik prowadził rozmowy
    chat_users = db.session.query(User).join(
        Message,
        or_(Message.sender_id == User.id, Message.receiver_id == User.id)
    ).filter(
        or_(Message.sender_id == user.id, Message.receiver_id == user.id)
    ).distinct().all()

    chat_users = [u for u in chat_users if u.email != current_user.email]

    return render_template('communication/chat.html', user=user, chat_users=chat_users)


@bp.route('/search_users')
def search_users():
    current_email = request.args.get('current_email')
    query = request.args.get('query', '')

    users = User.query.filter(
        User.email.ilike(f'%{query}%'),
        User.email != current_email
    ).all()

    return jsonify([{'email': user.email} for user in users])


@bp.route('/get_messages')
def get_messages():
    sender_email = request.args.get('sender')
    receiver_email = request.args.get('receiver')

    sender = User.query.filter_by(email=sender_email).first()
    receiver = User.query.filter_by(email=receiver_email).first()

    if not sender or not receiver:
        return jsonify([])

    messages = Message.query.filter(
        or_(
            (Message.sender_id == sender.id) & (Message.receiver_id == receiver.id),
            (Message.sender_id == receiver.id) & (Message.receiver_id == sender.id)
        )
    ).order_by(Message.timestamp).all()

    return jsonify([{
        'sender': message.sender.email,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for message in messages])
