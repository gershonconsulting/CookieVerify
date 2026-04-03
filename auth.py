"""
CookieVerify Auth - Registration, login, and session management
"""
import re
import bcrypt
import database


def validate_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email))


def register(email, password):
    """Create a new user account. Returns (result_dict, error_string)."""
    email = email.strip().lower()

    if not validate_email(email):
        return None, 'Invalid email address'
    if len(password) < 8:
        return None, 'Password must be at least 8 characters'

    if database.get_user_by_email(email):
        return None, 'An account with this email already exists'

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()
    user = database.create_user(email, password_hash)
    api_key = database.create_api_key(user['id'])
    token = database.create_session(user['id'])

    return {
        'user': {'id': user['id'], 'email': user['email'], 'plan': user['plan']},
        'token': token,
        'api_key': api_key['key']
    }, None


def login(email, password):
    """Authenticate a user. Returns (result_dict, error_string)."""
    email = email.strip().lower()

    user = database.get_user_by_email(email)
    if not user:
        return None, 'Invalid email or password'

    if not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return None, 'Invalid email or password'

    token = database.create_session(user['id'])
    return {
        'user': {'id': user['id'], 'email': user['email'], 'plan': user['plan']},
        'token': token
    }, None


def logout(token):
    """Invalidate a session token."""
    database.delete_session(token)
