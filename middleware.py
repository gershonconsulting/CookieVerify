"""
CookieVerify Middleware - Auth decorators for Flask routes
"""
from functools import wraps
from flask import request, jsonify, g
import database


def require_auth(f):
    """Decorator that requires a valid session token or API key."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
        if not token:
            return jsonify({'error': 'Unauthorized'}), 401

        if token.startswith('cv_'):
            user = database.get_user_by_api_key(token)
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            g.current_user = user
            g.auth_type = 'api_key'
            g.api_key_id = user.get('key_id')
        else:
            user = database.get_user_by_session(token)
            if not user:
                return jsonify({'error': 'Session expired or invalid'}), 401
            g.current_user = user
            g.auth_type = 'session'
            g.api_key_id = None

        return f(*args, **kwargs)
    return decorated


def optional_auth(f):
    """Decorator that attaches user info if a valid token is present, but does not require it."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
        g.current_user = None
        g.auth_type = None
        g.api_key_id = None

        if token:
            if token.startswith('cv_'):
                user = database.get_user_by_api_key(token)
                if user:
                    g.current_user = user
                    g.auth_type = 'api_key'
                    g.api_key_id = user.get('key_id')
            else:
                user = database.get_user_by_session(token)
                if user:
                    g.current_user = user
                    g.auth_type = 'session'

        return f(*args, **kwargs)
    return decorated
