"""
CookieVerify Database - SQLite schema and CRUD functions
"""
import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta

DATABASE_PATH = os.environ.get('DATABASE_PATH', './cookieverify.db')


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        plan TEXT DEFAULT 'free'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        key TEXT NOT NULL UNIQUE,
        name TEXT DEFAULT 'Default',
        created_at TEXT NOT NULL,
        last_used TEXT,
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS validations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        api_key_id INTEGER REFERENCES api_keys(id),
        cookie_hash TEXT NOT NULL,
        is_valid INTEGER NOT NULL,
        full_name TEXT,
        profile_url TEXT,
        company TEXT,
        title TEXT,
        vanity_name TEXT,
        error_msg TEXT,
        source TEXT DEFAULT 'web',
        created_at TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────────────────────────────

def create_user(email, password_hash):
    conn = get_db()
    try:
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute(
            'INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)',
            (email, password_hash, now)
        )
        user_id = c.lastrowid
        conn.commit()
        return {'id': user_id, 'email': email, 'created_at': now, 'plan': 'free'}
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_db()
    try:
        row = conn.execute(
            'SELECT * FROM users WHERE email = ? AND is_active = 1', (email,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            'SELECT * FROM users WHERE id = ? AND is_active = 1', (user_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ── Sessions ───────────────────────────────────────────────────────────────────

def create_session(user_id):
    conn = get_db()
    try:
        token = secrets.token_hex(32)
        now = datetime.utcnow()
        expires = now + timedelta(days=30)
        conn.execute(
            'INSERT INTO sessions (id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)',
            (token, user_id, now.isoformat(), expires.isoformat())
        )
        conn.commit()
        return token
    finally:
        conn.close()


def get_user_by_session(token):
    conn = get_db()
    try:
        now = datetime.utcnow().isoformat()
        row = conn.execute('''
            SELECT u.* FROM users u
            JOIN sessions s ON s.user_id = u.id
            WHERE s.id = ? AND s.expires_at > ? AND u.is_active = 1
        ''', (token, now)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_session(token):
    conn = get_db()
    try:
        conn.execute('DELETE FROM sessions WHERE id = ?', (token,))
        conn.commit()
    finally:
        conn.close()


# ── API Keys ───────────────────────────────────────────────────────────────────

def create_api_key(user_id, name='Default'):
    conn = get_db()
    try:
        key = 'cv_' + secrets.token_hex(32)
        now = datetime.utcnow().isoformat()
        c = conn.cursor()
        c.execute(
            'INSERT INTO api_keys (user_id, key, name, created_at) VALUES (?, ?, ?, ?)',
            (user_id, key, name, now)
        )
        key_id = c.lastrowid
        conn.commit()
        return {'id': key_id, 'key': key, 'name': name, 'created_at': now, 'last_used': None}
    finally:
        conn.close()


def get_user_api_keys(user_id):
    conn = get_db()
    try:
        rows = conn.execute(
            'SELECT * FROM api_keys WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_user_by_api_key(key):
    conn = get_db()
    try:
        now = datetime.utcnow().isoformat()
        row = conn.execute('''
            SELECT u.*, ak.id as key_id FROM users u
            JOIN api_keys ak ON ak.user_id = u.id
            WHERE ak.key = ? AND ak.is_active = 1 AND u.is_active = 1
        ''', (key,)).fetchone()
        if row:
            conn.execute(
                'UPDATE api_keys SET last_used = ? WHERE key = ?', (now, key)
            )
            conn.commit()
            return dict(row)
        return None
    finally:
        conn.close()


def revoke_api_key(key_id, user_id):
    conn = get_db()
    try:
        conn.execute(
            'UPDATE api_keys SET is_active = 0 WHERE id = ? AND user_id = ?',
            (key_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()


# ── Validations ────────────────────────────────────────────────────────────────

def save_validation(user_id, cookie_value, result, source='web', api_key_id=None):
    conn = get_db()
    try:
        now = datetime.utcnow().isoformat()
        cookie_hash = hashlib.sha256(cookie_value.encode()).hexdigest()[:16]
        full_name = (
            result.get('fullName')
            or f"{result.get('firstName', '')} {result.get('lastName', '')}".strip()
            or None
        )
        conn.execute('''
            INSERT INTO validations
            (user_id, api_key_id, cookie_hash, is_valid, full_name, profile_url,
             company, title, vanity_name, error_msg, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, api_key_id, cookie_hash,
            1 if result.get('isValid') else 0,
            full_name,
            result.get('profileUrl'),
            result.get('company'),
            result.get('title') or result.get('headline'),
            result.get('vanityName'),
            result.get('error'),
            source,
            now
        ))
        conn.commit()
    finally:
        conn.close()


def get_user_stats(user_id):
    conn = get_db()
    try:
        total = conn.execute(
            'SELECT COUNT(*) FROM validations WHERE user_id = ?', (user_id,)
        ).fetchone()[0]
        valid = conn.execute(
            'SELECT COUNT(*) FROM validations WHERE user_id = ? AND is_valid = 1', (user_id,)
        ).fetchone()[0]
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).isoformat()
        this_month = conn.execute(
            'SELECT COUNT(*) FROM validations WHERE user_id = ? AND created_at >= ?',
            (user_id, month_start)
        ).fetchone()[0]
        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'this_month': this_month
        }
    finally:
        conn.close()


def get_user_history(user_id, page=1, limit=20, filter_by='all'):
    conn = get_db()
    try:
        offset = (page - 1) * limit
        conditions = ['v.user_id = ?']
        params = [user_id]
        if filter_by == 'valid':
            conditions.append('v.is_valid = 1')
        elif filter_by == 'invalid':
            conditions.append('v.is_valid = 0')
        where = 'WHERE ' + ' AND '.join(conditions)
        rows = conn.execute(f'''
            SELECT v.*, ak.name as api_key_name FROM validations v
            LEFT JOIN api_keys ak ON ak.id = v.api_key_id
            {where}
            ORDER BY v.created_at DESC
            LIMIT ? OFFSET ?
        ''', params + [limit, offset]).fetchall()
        total = conn.execute(
            f'SELECT COUNT(*) FROM validations v {where}', params
        ).fetchone()[0]
        return {'items': [dict(r) for r in rows], 'total': total, 'page': page, 'limit': limit}
    finally:
        conn.close()
