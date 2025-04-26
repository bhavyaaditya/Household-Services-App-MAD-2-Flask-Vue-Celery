from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for
from flask_security import login_user, logout_user, hash_password, login_required, current_user, roles_required
from flask_security.utils import verify_password
from sqlalchemy.exc import IntegrityError
from app.models import db, User, Role, Service, roles_users
from datetime import datetime
import jwt
from icecream import ic
import uuid

from app.auth import auth
from app.cities import cities

# from household_services_app import app as auth

# auth = current_app

@auth.route("/", methods=['GET','POST'])
def home():
    return jsonify({'status':'success'}) # render_template("auth/index.html")

@auth.route('/login/', methods=['GET','POST'])
def login():
    if request.method=="GET":
        print("GETTING!!!!!!!!!!!!!!!!!")
        return jsonify({'message': 'Login page'}), 200

    elif request.method=="POST":
        print("POSTING!!!!!!!!!!!!!!!!!")
        # data = request.form
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        ic(data.get('email'))
        ic(data.get('password'))
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        ic(data['password'])
        ic(user.password)
        ic(user.check_password(data['password']))

        if not user or not verify_password(data['password'], user.password): # user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # if not user.activated:
        #     return jsonify({'message': 'Account is deactivated'}), 401
                
        login_user(user)
        
        return jsonify({
        'message': 'Login successful',
        'role': user.roles[0].name if user.roles else None,
        'redirect_url': url_for(f'{user.roles[0].name}.{user.roles[0].name}_dashboard') if user.roles else None,
        "activated": user.activated,
        }), 200

@auth.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out'}), 200

@auth.route('/register/user', methods=['GET','POST'])
def register_user():
    # if request.method=='GET':
    #     return render_template('auth/register_user.html', cities=cities)

    if request.method=='POST':
        data = request.form
        
        required_fields = ['email', 'password', 'first_name', 'last_name']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        try:
            # Create new user
            user = User(
                email=data['email'],
                password=hash_password(data['password']),
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone_number'],
                address=data['address'],
                activated=True,
                confirmed_at=datetime.utcnow(),
                fs_uniquifier = str(uuid.uuid4())
            )
            
            # Assign user role
            user_role = Role.query.filter_by(name='user').first()
            user.roles.append(user_role)
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user.id
            }), 201
            
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Email already registered'}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Registration failed'}), 500

@auth.route('/register/tradie', methods=['GET','POST'])
def register_tradie():
    # if request.method=='GET':
    #     global Service  # Without this line the next line is giving error -> UnboundLocalError: local variable 'Service' referenced before assignment
    #     services = [service.name for service in Service.query.filter_by(activated=True).all()]
    #     ic(services)
    #     return render_template('auth/register_tradie.html', services=services, cities=cities)

    if request.method=='POST':
        data = request.form
        ic(data)
        required_fields = [
            'email', 'password', 'first_name', 'last_name', 
            'years_of_experience', 'service_category', 'hourly_rate',
        ]
        
        # Validate form: Compulsory fields must be present
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        ic("Form validation passed")
        try:
            # Create new tradie user
            tradie = User(
                email=data['email'],
                password=hash_password(data['password']),
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number= data['phone_number'],
                address=data['address'],
                hourly_rate=data['hourly_rate'],
                years_of_experience=int(data['years_of_experience']),
                activated=False,
                confirmed_at=datetime.utcnow(),
                fs_uniquifier = str(uuid.uuid4())
            )
            ic(tradie)
            # Assign tradie role
            tradie_role = Role.query.filter_by(name='tradie').first()
            ic(tradie_role)
            tradie.roles.append(tradie_role)
            ic("added role")
            
            # Add service category
            category = Service.query.filter_by(name=data['service_category']).first()
            ic(category)
            tradie.service_categories.append(category)
            
            db.session.add(tradie)
            db.session.commit()
            
            return jsonify({
                'message': 'tradie registered successfully',
                'user_id': tradie.id
            }), 201
            
        except IntegrityError:
            db.session.rollback()
            return jsonify({'message': 'Email already registered'}), 409
        except Exception as e:
            db.session.rollback()
            ic(e)
            return jsonify({'message': 'Registration failed'}), 500


#* ----------------VUE------------------
@auth.route('/api/cities')
def get_cities():
    return jsonify(cities), 200

@auth.route('/api/services')
def get_services():
    services_ = Service.query.filter_by(activated=True).all()
    services=[service.as_dict() for service in services_]
    return jsonify(services), 200