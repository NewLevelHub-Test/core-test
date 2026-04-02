import re
import bleach


def validate_registration(data):
    errors = []

    if not data.get('username') or len(data['username']) < 3:
        errors.append('Имя пользователя должно содержать минимум 3 символа')

    has_email = data.get('email')
    has_phone = data.get('phone')

    if not has_email and not has_phone:
        errors.append('Укажите email или номер телефона')

    if has_email and not _is_valid_email(data['email']):
        errors.append('Некорректный email')

    if has_phone and not _is_valid_phone(data['phone']):
        errors.append('Некорректный номер телефона')

    if not data.get('password') or len(data['password']) < 6:
        errors.append('Пароль должен содержать минимум 6 символов')

    age = data.get('age')
    if age is not None:
        if not isinstance(age, int) or age < 5 or age > 12:
            errors.append('Возраст должен быть от 5 до 12 лет')

    return errors if errors else None


def validate_fen(fen):
    if not fen or not isinstance(fen, str):
        return False
    parts = fen.split()
    if len(parts) != 6:
        return False
    rows = parts[0].split('/')
    return len(rows) == 8


def _is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def _is_valid_phone(phone):
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(r'^\+?\d{10,15}$', cleaned))

def clean_html(text):
    if not text or not isinstance(text, str):
        return text
    return bleach.clean(text, tags=[], strip=True)
