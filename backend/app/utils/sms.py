import random
import string
from datetime import datetime, timedelta


def generate_sms_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def code_expiry(minutes=5):
    return datetime.utcnow() + timedelta(minutes=minutes)


def send_sms(phone: str, code: str) -> bool:
    """
    Placeholder for real SMS provider integration (Twilio, SMS.ru, etc.).
    In development returns True; replace with actual API call in production.
    """
    print(f'[SMS] → {phone}: Ваш код: {code}')
    return True
