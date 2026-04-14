import random
import string
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def generate_sms_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def code_expiry(minutes=5):
    return datetime.utcnow() + timedelta(minutes=minutes)


def send_sms(phone: str, code: str) -> bool:
    provider_url = os.environ.get("SMS_PROVIDER_URL")
    api_key = os.environ.get("SMS_API_KEY")
    sender = os.environ.get("SMS_SENDER", "RO-CHESS")

    if not provider_url or not api_key:
        logger.warning("SMS provider is not configured")
        return False

    payload = {
        "to": phone,
        "message": f"Ваш код подтверждения: {code}",
        "sender": sender,
    }
    data = urlencode(payload).encode("utf-8")
    req = Request(
        provider_url,
        data=data,
        headers={"Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception as exc:
        logger.error("Failed to send SMS: %s", exc)
        return False


def send_recovery_email(email: str, code: str) -> bool:
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM", smtp_user or "")

    if not smtp_host or not smtp_user or not smtp_password or not smtp_from:
        logger.warning("SMTP is not configured")
        return False

    message = EmailMessage()
    message["Subject"] = "Код восстановления доступа"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(f"Ваш код восстановления: {code}. Код действует 10 минут.")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True
    except Exception as exc:
        logger.error("Failed to send recovery email: %s", exc)
        return False
