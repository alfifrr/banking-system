# decorator to wrap func. and handle things
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User


def require_active_account(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_active:
            return jsonify({
                'error': 'Account not activated',
                'message': ' Please activate your account first'
            }), 403

        return f(*args, **kwargs)
    return decorated_function
