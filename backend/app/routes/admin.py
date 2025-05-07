# File for fetching admins (needs fixing or replacing)

from flask import Blueprint, jsonify, request, session
from create_app import db
from app.models.db_models import *
from app.routes.auth import admin_login_required
from app.routes.utils import *

# Create a Blueprint for authentication routess
admin = Blueprint('admin', __name__)

# Dashboard Route
@admin.route('/dashboard', methods=['GET'])
@admin_login_required
def Dashboard():
    user = db.session.query(User).filter_by(user_id=session['user_id']).first()
    return jsonify({'message': 'Welcome to the admin Dashboard {}!'.format(user.first_name)})


# Route to show all admins in the system
@admin.route('/show_admins', methods=['GET'])
@admin_login_required
def show_agents():
    try:
        users = db.session.query(User).filter_by(user_type='admin').all()
        agents = [
            {
                'admin_id': user.user_id,
                'firstname': user.first_name,
                'lastname': user.last_name,
                'email': user.email
            }
            for user in users
        ]
        return jsonify({'type':'success', 'message': 'Admins fetched successfully', 'data':agents}), 200
    except Exception as e:
        return jsonify({'type':'error','message': 'An internal error occured.\n {}'.format(e)}), 500
    
    return data