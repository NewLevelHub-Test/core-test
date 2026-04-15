from datetime import datetime

from flask_jwt_extended import create_access_token, create_refresh_token

from app import db
from app.models.user import User
from app.utils.validators import validate_registration
from app.utils.sms import generate_sms_code, code_expiry, send_sms, send_recovery_email
from app.utils.helpers import clean_html  

class AuthService:

    @staticmethod
    def register(data):
        errors = validate_registration(data)
        if errors:
            return {'error': errors}, 400

        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return {'error': 'Email уже зарегистрирован'}, 409

        if data.get('phone') and User.query.filter_by(phone=data['phone']).first():
            return {'error': 'Телефон уже зарегистрирован'}, 409

        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Имя пользователя занято'}, 409

        user = User(
            username=clean_html(data['username']),
            email=data.get('email'),
            phone=data.get('phone'),
            age=data.get('age'),
            role='student',
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, 201

    @staticmethod
    def login(data):
        email = data.get('email')
        phone = data.get('phone')
        username = data.get('username')

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        if not user and phone:
            user = User.query.filter_by(phone=phone).first()
        if not user and username:
            user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(data.get('password', '')):
            return {'error': 'Неверные учётные данные'}, 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, 200

    # --- SMS auth flow ---

    @staticmethod
    def send_sms_code(phone):
        if not phone:
            return {'error': 'Укажите номер телефона'}, 400

        import re as _re
        cleaned = _re.sub(r'[\s\-\(\)]', '', phone)
        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User.query.filter_by(phone=cleaned).first()
        if not user and cleaned.startswith('+'):
            user = User.query.filter_by(phone=cleaned[1:]).first()
        if not user and not cleaned.startswith('+'):
            user = User.query.filter_by(phone='+' + cleaned).first()
        if not user:
            return {'error': 'Пользователь с таким номером не найден'}, 404

        code = generate_sms_code()
        user.sms_code = code
        user.sms_code_expires = code_expiry()
        db.session.commit()

        send_sms(phone, code)
        return {'message': 'Код отправлен'}, 200

    @staticmethod
    def verify_sms_code(phone, code):
        if not phone or not code:
            return {'error': 'Укажите телефон и код'}, 400

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        if user.sms_code != code:
            return {'error': 'Неверный код'}, 401

        if user.sms_code_expires and user.sms_code_expires < datetime.utcnow():
            return {'error': 'Код истёк'}, 401

        user.sms_code = None
        user.sms_code_expires = None
        db.session.commit()

        return {'verified': True}, 200

    @staticmethod
    def login_by_phone(phone, code):
        if not phone or not code:
            return {'error': 'Укажите телефон и код'}, 400

        user = User.query.filter_by(phone=phone).first()
        if not user:
            return {'error': 'Пользователь не найден'}, 404

        if user.sms_code != code:
            return {'error': 'Неверный код'}, 401

        if user.sms_code_expires and user.sms_code_expires < datetime.utcnow():
            return {'error': 'Код истёк'}, 401

        user.sms_code = None
        user.sms_code_expires = None
        db.session.commit()

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
        }, 200

    # --- Recovery ---

    @staticmethod
    def send_recovery_code(email=None, phone=None):
        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif phone:
            user = User.query.filter_by(phone=phone).first()

        if not user:
            return {'error': 'Пользователь не найден'}, 404

        code = generate_sms_code()
        user.recovery_code = code
        user.recovery_code_expires = code_expiry(minutes=10)
        db.session.commit()

        sent = False
        if phone:
            sent = send_sms(phone, code)
        elif email:
            sent = send_recovery_email(email, code)

        if not sent:
            return {'error': 'Не удалось отправить код восстановления'}, 503

        return {'message': 'Код восстановления отправлен'}, 200

    @staticmethod
    def confirm_recovery(data):
        email = data.get('email')
        phone = data.get('phone')
        code = data.get('code')
        new_password = data.get('new_password')

        if not code or not new_password:
            return {'error': 'Укажите код и новый пароль'}, 400

        user = None
        if email:
            user = User.query.filter_by(email=email).first()
        elif phone:
            user = User.query.filter_by(phone=phone).first()

        if not user:
            return {'error': 'Пользователь не найден'}, 404

        if user.recovery_code != code:
            return {'error': 'Неверный код'}, 401

        if user.recovery_code_expires and user.recovery_code_expires < datetime.utcnow():
            return {'error': 'Код истёк'}, 401

        if len(new_password) < 6:
            return {'error': 'Пароль должен содержать минимум 6 символов'}, 400

        user.set_password(new_password)
        user.recovery_code = None
        user.recovery_code_expires = None
        db.session.commit()

        return {'message': 'Пароль успешно изменён'}, 200

    # --- Common ---

    @staticmethod
    def refresh_token(identity):
        access_token = create_access_token(identity=identity)
        return {'access_token': access_token}, 200

    @staticmethod
    def get_current_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}, 404
        return {'user': user.to_dict()}, 200
