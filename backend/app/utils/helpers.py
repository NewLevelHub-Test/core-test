from datetime import datetime


def format_datetime(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def paginate_query(query, page=1, per_page=20):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page,
    }


def elo_update(rating_a, rating_b, score_a, k=32):
    """Calculate new ELO ratings. score_a: 1=win, 0=loss, 0.5=draw"""
    expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    expected_b = 1 - expected_a
    score_b = 1 - score_a

    new_a = round(rating_a + k * (score_a - expected_a))
    new_b = round(rating_b + k * (score_b - expected_b))

    return new_a, new_b
