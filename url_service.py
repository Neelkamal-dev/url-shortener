import random
import string
import re
from datetime import datetime
from sqlalchemy import text

CHARSET = string.ascii_letters + string.digits
CODE_LENGTH = 6


def generate_short_code(length=CODE_LENGTH):
    return ''.join(random.choices(CHARSET, k=length))


def is_valid_url(url: str) -> bool:
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )
    return bool(pattern.match(url))


def is_valid_custom_code(code: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9-]{3,20}$', code))


def create_short_url(db, original_url: str, custom_code: str = None) -> dict:
    if not is_valid_url(original_url):
        return {'error': 'Invalid URL. Please include http:// or https://'}

    if custom_code:
        if not is_valid_custom_code(custom_code):
            return {'error': 'Custom code must be 3-20 characters (letters, numbers, hyphens only)'}

        existing = db.execute(
            text('SELECT id FROM urls WHERE short_code = :code'),
            {'code': custom_code}
        ).fetchone()

        if existing:
            return {'error': f'Custom code "{custom_code}" is already taken'}

        short_code = custom_code
    else:
        # Return existing short code if URL already shortened
        existing = db.execute(
            text('SELECT short_code, clicks, created_at FROM urls WHERE original_url = :url'),
            {'url': original_url}
        ).fetchone()

        if existing:
            return {
                'short_code': existing.short_code,
                'original_url': original_url,
                'clicks': existing.clicks,
                'created_at': str(existing.created_at),
                'message': 'URL already shortened'
            }

        # Generate unique code
        for _ in range(10):
            short_code = generate_short_code()
            taken = db.execute(
                text('SELECT id FROM urls WHERE short_code = :code'),
                {'code': short_code}
            ).fetchone()
            if not taken:
                break
        else:
            return {'error': 'Could not generate a unique code. Please try again.'}

    db.execute(
        text('INSERT INTO urls (original_url, short_code) VALUES (:url, :code)'),
        {'url': original_url, 'code': short_code}
    )
    db.commit()

    return {
        'short_code': short_code,
        'original_url': original_url,
        'clicks': 0,
        'created_at': datetime.utcnow().isoformat()
    }


def get_original_url(db, short_code: str):
    row = db.execute(
        text('SELECT original_url FROM urls WHERE short_code = :code'),
        {'code': short_code}
    ).fetchone()

    if not row:
        return None

    db.execute(
        text('UPDATE urls SET clicks = clicks + 1, last_accessed = CURRENT_TIMESTAMP WHERE short_code = :code'),
        {'code': short_code}
    )
    db.commit()
    return row.original_url


def get_all_urls(db) -> list:
    rows = db.execute(
        text('SELECT original_url, short_code, clicks, created_at, last_accessed FROM urls ORDER BY created_at DESC')
    ).fetchall()
    return [dict(r._mapping) for r in rows]


def get_url_stats(db, short_code: str):
    row = db.execute(
        text('SELECT original_url, short_code, clicks, created_at, last_accessed FROM urls WHERE short_code = :code'),
        {'code': short_code}
    ).fetchone()
    return dict(row._mapping) if row else None
