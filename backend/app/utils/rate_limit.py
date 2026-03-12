import time
from functools import wraps
from collections import defaultdict

from flask import request, jsonify

_request_counts = defaultdict(list)

MAX_REQUESTS = 60
WINDOW_SECONDS = 60


def rate_limit(max_requests=MAX_REQUESTS, window=WINDOW_SECONDS):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()

            _request_counts[ip] = [
                t for t in _request_counts[ip] if now - t < window
            ]

            if len(_request_counts[ip]) >= max_requests:
                return jsonify({'error': 'Слишком много запросов'}), 429

            _request_counts[ip].append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


_sms_counts = defaultdict(list)

SMS_MAX = 3
SMS_WINDOW = 300  # 5 min


def sms_rate_limit(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr
        phone = (request.get_json() or {}).get('phone', ip)
        key = f'{ip}:{phone}'
        now = time.time()

        _sms_counts[key] = [t for t in _sms_counts[key] if now - t < SMS_WINDOW]

        if len(_sms_counts[key]) >= SMS_MAX:
            return jsonify({'error': 'Слишком много запросов на отправку кода. Попробуйте через 5 минут'}), 429

        _sms_counts[key].append(now)
        return fn(*args, **kwargs)
    return wrapper
