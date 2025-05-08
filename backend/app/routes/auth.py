# Authentication routes

from flask import Blueprint, request, jsonify, session
from create_app import db, bcrypt
from app.models.db_models import *
from functools import wraps

# Create a Blueprint for authentication routess
auth_bp = Blueprint('auth', __name__)

#Custom decorator for login manager
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("user details", session)
        if "user_id" not in session:
            return jsonify({'type':'error',"message":"Unauthorized access, please log in"}),401
        return f(*args, **kwargs)
    return decorated_function

#Custom decorator for admin login manager
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['user_type'] != 'admin':
            return jsonify({'type':'error',"message":"Permission Denied: Unauthorized access"}),401
        return f(*args, **kwargs)
    return decorated_function

#Custom decorator for agent login manager
def agent_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['user_type'] != 'agent':
            return jsonify({'type':'error',"message":"Permission Denied: Unauthorized access"}),401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # Get JSON data from request
    firstname = data.get("fname")
    lastname = data.get('lname')
    email = data.get('email')
    password = data.get('pass')
    
    # Check if the email exists in the database
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        return jsonify({'type':'error','message': 'User already exists for this email, please log in.'}), 409
    
    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(first_name=firstname, last_name=lastname, user_type="applicant", email=email, password_hash=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'type' : 'success',
            'message': 'User created successfully!',
            'data': {
                'id': new_user.user_id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'type':'error','message': 'An unexpected error occurred: {}'.format(e)}), 500

@auth_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()  # Get JSON data from request
    firstname = data.get("fname")
    lastname = data.get('lname')
    email = data.get('email')
    password = data.get('pass')

    try:
        user = db.session.query(User).filter_by(email=email).first()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.first_name = firstname
        user.last_name = lastname
        user.user_type = "applicant"
        user.email=email
        user.password_hash=hashed_password
        db.session.commit()
        return jsonify({
            'type' : 'success',
            'message': 'Profile updated successfully!',
            'data': {
                'id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'type':'error','message': 'An unexpected error occurred: {}'.format(e)}), 500
    

@auth_bp.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if 'user_id' in session:
            return(jsonify({
                    'type':'error', 
                    'message':f"User ID {session['user_id']} is already in the session",
                    'data' : {'user_id': session['user_id'], 'user_type':session['user_type']}
                    })), 409
        data = request.get_json()  
        email = data.get('email')
        password = data.get('password')
        try:
            # Check if user exists
            user = db.session.query(User).filter_by(email=email).first()

            if user and bcrypt.check_password_hash(user.password_hash, password):
                session['user_id'] = user.user_id
                session['user_type'] = user.user_type
                print("login", session)
                return(jsonify({
                    'type':'success', 
                    'message':"Log in successfull",
                    'data' : {'user_id': session['user_id'],'user_type':session['user_type']}
                    })), 200
            else:
                return jsonify({'type':'error','message': 'Invalid credentials. Please try again'}), 401

        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({'type':'error','message': 'An internal error occured.\n {}'.format(e)}), 500
    
    if request.method == 'GET':
        if 'user_id' in session:
            return(jsonify({
                    'type':'success', 
                    'message':f"User ID {session['user_id']} is in the session",
                    'data' : {'user_id': session['user_id'],'user_type':session['user_type']}
                    })), 200
        else:
            return(jsonify({
                    'type':'error', 
                    'message':"No user is logged",
                    'data' : {'user_id': None}
                    })), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    print('Session before logout:', session)  # Check session state
    if 'user_id' not in session:
        print('No user logged in during logout attempt.')
        return jsonify({'type':'error','message': 'No user logged in.'}), 400
    session.pop('user_id', None)
    session.pop('user_type', None)
    session.clear()
    print('Session after logout:', session)
    return jsonify({'type':'success','message': 'Logged out successfully!'}), 200