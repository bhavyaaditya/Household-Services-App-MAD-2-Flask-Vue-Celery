from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from datetime import datetime
# from app import db
import uuid

db = SQLAlchemy()

# Association tables for many-to-many relationships
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

services_tradies = db.Table(
    'services_tradies',
    db.Column('tradie_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('service_id', db.Integer(), db.ForeignKey('service.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    activated = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    
    # User profile fields
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    state_ = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)

    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)  # Required for Flask-Security 4+
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users,
                          backref=db.backref('user', lazy='dynamic'))
    
    # Professional-specific fields
    hourly_rate = db.Column(db.Float)   # One tradie is good at only one service
    years_of_experience = db.Column(db.Integer)
    # is_available = db.Column(db.Boolean, default=True)
    service_categories = db.relationship('Service', 
                                      secondary=services_tradies,
                                      backref=db.backref('professionals', lazy='dynamic'))
    
    # Services provided (for professionals)
    services_provided = db.relationship('ServiceRequest', 
                                      backref='professional',
                                      foreign_keys='ServiceRequest.tradie_id',
                                      lazy='dynamic')
    
    # Services received (for users)
    services_received = db.relationship('ServiceRequest',
                                      backref='client',
                                      foreign_keys='ServiceRequest.client_id',
                                      lazy='dynamic')
    
    def check_password(self, password):
        flag = password==self.password
        return flag
    
    @property
    def is_active(self):
        """
        In Flask-Security, `active` and `is_active` are properties of the UserMixin class. When logging in a deactivated user, Flask is confusing them to be unauthenticated and then is causing redirection error like:

        127.0.0.1 - - [30/Mar/2025 12:18:49] "POST /login/ HTTP/1.1" 200 -
        127.0.0.1 - - [30/Mar/2025 12:18:50] "GET /tradie/profile HTTP/1.1" 302 -
        127.0.0.1 - - [30/Mar/2025 12:18:50] "GET /tradie/dashboard HTTP/1.1" 302 -
        127.0.0.1 - - [30/Mar/2025 12:18:50] "GET /login?next=/tradie/profile HTTP/1.1" 200 -

        Change this property in user to True by default to avoid this issue. Had earlier cahnged the field `active` in User model to `is_active` but both names are used in Flask-Security. So, this is the only way to avoid the issue and also rename the field again to `activated`.
        """
        return True
    @property
    def active(self):
        return True
    
    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "address": self.address,
            "location": self.location,
            "hourly_rate": self.hourly_rate,
            "years_of_experience": self.years_of_experience,
            "activated": self.activated,
            "roles": [role.name for role in self.roles],
            "service_categories": [{"id": s.id, "name": s.name} for s in self.service_categories]
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, default=1, nullable=False)
    activated = db.Column(db.Boolean, default=True)
    
    # Services in this category
    services = db.relationship('ServiceRequest', backref='category', lazy='dynamic')

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "base_price": self.base_price,
            "activated": self.activated
        }


applied_tradies_table = db.Table(
    'applied_tradies',
    db.Column('tradie_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service_request_id', db.Integer, db.ForeignKey('service_request.id'))
)

requested_tradies_table = db.Table(
    'requested_tradies',
    db.Column('tradie_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('service_request_id', db.Integer, db.ForeignKey('service_request.id'))
)

class ServiceRequest(db.Model):
    """
    A service request is created by a user who wants to avail a certain type of service on a certain date. 

    The status of a service request, at any point in time, can be one of the below:
    1. `open`       - Service request raised by user 
    2. `cancelled`  - Service request cancelled by user before being `booked`
    3. `booked`     - Tradie has been finalized by the user from the list of interested tradies
    4. `due_today`  - A booked request is due to be done today
    5. `closed`     - Tradie has closed the service request on/after the due date

    Sanity checks:
        - If `tradie_id` is `null`, status can only be either `open` or `cancelled`.
        - Alternatively, if `tradie_id` is not `null`, then status cannot be `open` or `cancelled`
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    tradie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    
    # Service Request details
    created_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the service request was created
    due_date = db.Column(db.DateTime)   # Date when the user wants the service to be done
    status = db.Column(db.String(20), default='open')
    estimated_hours = db.Column(db.Float)
    hourly_rate = db.Column(db.Float)
    total_cost = db.Column(db.Float)
    
    # Service details
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    
    # Review
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    review_date = db.Column(db.DateTime)

    applied_tradies = db.relationship(
    'User',
    secondary=applied_tradies_table,  # Define a separate association table
    backref=db.backref('applied_requests', lazy='dynamic')
    )

    requested_tradies = db.relationship(
        'User',
        secondary=requested_tradies_table,
        backref=db.backref('requested_requests', lazy='dynamic')
    )

    def as_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "tradie_id": self.tradie_id,
            "service_id": self.service_id,
            "created_date": self.created_date.strftime('%Y-%m-%d') if self.created_date else None,
            "due_date": self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            "status": self.status,
            "estimated_hours": self.estimated_hours,
            "total_cost": self.total_cost,
            "description": self.description,
            "location": self.location,
            "rating": self.rating,
            "review": self.review,
            "review_date": self.review_date.strftime('%Y-%m-%d') if self.review_date else None,

            "applied_tradies": [tradie.as_dict() for tradie in self.applied_tradies],
            "client": User.query.get(self.client_id).as_dict(),
            "tradie": User.query.get(self.tradie_id).as_dict() if self.tradie_id else None,
            "tradie_name": User.query.get(self.tradie_id).first_name + " " + User.query.get(self.tradie_id).last_name if self.tradie_id else None,
            "service_category": Service.query.get(self.service_id).as_dict(),
            "service_name": Service.query.get(self.service_id).name,
            "name":Service.query.get(self.service_id).name,
        }


def init_db(app):
    """Initialize the database and create the admin role and user"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create roles if they don't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
        
        tradie_role = Role.query.filter_by(name='tradie').first()
        if not tradie_role:
            tradie_role = Role(name='tradie', description='Service Professional')
            db.session.add(tradie_role)
        
        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Service User')
            db.session.add(user_role)
        
        #!START: Create test users
        # 1. Admin user
        admin_user = User.query.filter_by(email='admin@test.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@test.com',
                password='admin123',
                activated=True,
                confirmed_at=datetime.utcnow(),
                first_name='Admin',
                last_name='User',
                phone_number='1234567890',
                address='123 Admin St',
                fs_uniquifier = str(uuid.uuid4())
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)

        # 2. Professional user
        tradie = User.query.filter_by(email='professional@test.com').first()
        if not tradie:
            tradie = User(
                email='professional@test.com',
                password='prof123',
                activated=True,
                confirmed_at=datetime.utcnow(),
                first_name='Pro',
                last_name='Service',
                phone_number='0987654321',
                address='456 Pro Ave',
                hourly_rate=50.0,
                years_of_experience=5,
                is_available=True,
                fs_uniquifier = str(uuid.uuid4())
            )
            tradie.roles.append(tradie_role)
            
            # Create and assign service categories
            plumbing = Service.query.filter_by(name='Plumbing').first()
            if not plumbing:
                plumbing = Service(
                    name='Plumbing',
                    description='All types of plumbing services',
                    base_price=1
                )
                db.session.add(plumbing)
            
            carpentry = Service.query.filter_by(name='Carpentry').first()
            if not carpentry:
                carpentry = Service(
                    name='Carpentry',
                    description='Professional carpentry services',
                    base_price=1
                )
                db.session.add(carpentry)
            
            # tradie.service_categories.extend([plumbing, carpentry])
            tradie.service_categories.append(plumbing)
            db.session.add(tradie)

        # 3. Regular user
        regular_user = User.query.filter_by(email='user@test.com').first()
        if not regular_user:
            regular_user = User(
                email='user@test.com',
                password='user123',
                activated=True,
                confirmed_at=datetime.utcnow(),
                first_name='Regular',
                last_name='User',
                phone_number='5555555555',
                address='789 User Blvd',
                fs_uniquifier = str(uuid.uuid4())
            )
            regular_user.roles.append(user_role)
            db.session.add(regular_user)

        db.session.commit()
        #!END: Create test users