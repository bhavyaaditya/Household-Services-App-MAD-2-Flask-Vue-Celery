from flask import Blueprint, request, jsonify, current_app, render_template, render_template_string, flash, redirect, url_for, abort
from flask_security import login_user, logout_user, hash_password, login_required, current_user, roles_required
from flask_security.utils import verify_password
from sqlalchemy.exc import IntegrityError
from app.models import db, User, Role, Service, ServiceRequest, services_tradies, roles_users
from datetime import datetime
import jwt
from icecream import ic
import uuid

from app.user import user

from app.cities import cities
import re
from datetime import date

@user.route("/user/dashboard", methods=["GET","POST"])
@login_required
@roles_required('user')
def user_dashboard():
    services = Service.query.filter(Service.activated).all()
    ic(services)
    service_requests_ = ServiceRequest.query.filter_by(client_id=current_user.id).all()
    
    today = date.today()

    service_requests = []
    for req in service_requests_:
        # Dynamically determine status for display purposes
        req_dict = req.as_dict()
        
        # Check if status is booked and due_date is today
        if req.status == 'booked' and req.due_date.date() == today:
            req_dict['status'] = 'due_today'
        service_requests.append(req_dict)

    return jsonify({
        "services": [s.as_dict() for s in services],
        "service_requests": service_requests,
        "cities": cities,
        "activated":current_user.activated
    })

@user.route('/create_request', methods=['POST'])
@login_required
@roles_required('user')
def create_request():
    if not current_user.activated:
        return jsonify({'message': 'Your account has been deactivated by admin. You cannot create new service requests.'}), 403
    data = request.form
    new_request = ServiceRequest(
        client_id=current_user.id,
        service_id=data.get("service_id"),
        location=data.get("location"),
        description=data.get("description"),
        due_date=datetime.strptime(data.get("due_date"), '%Y-%m-%d'),
        status="open",
        hourly_rate=data.get("hourly_rate"),
        estimated_hours=data.get("estimated_hours"),
        total_cost=data.get("total_cost")
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"status": "success"})

@user.route('/cancel_request', methods=['POST'])
@login_required
@roles_required('user')
def cancel_request():
    data = request.form
    request_id = data.get("request_id")
    service_request = ServiceRequest.query.get(request_id)

    if not service_request or service_request.client_id != current_user.id:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    service_request.status = "cancelled"
    db.session.commit()
    return jsonify({"status": "success"})

@user.route('/view_applications/<request_id>/', methods=['GET','POST'])
@login_required
@roles_required('user')
def view_applicants(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id, client_id=current_user.id).first_or_404()
    created_date = service_request.created_date.strftime('%d %B %Y')
    due_date = service_request.due_date.strftime('%d %B %Y')
    service_type = Service.query.get(service_request.service_id).name
    applicants = service_request.applied_tradies
    return jsonify({
        "service_request": service_request.as_dict(),
        "created_date": created_date,
        "due_date": due_date,
        "service_type": service_type,
        "applicants": [t.as_dict() for t in applicants]
    })

@user.route('/service_requests/<int:request_id>/select_tradie', methods=['POST'])
@login_required
@roles_required('user')
def select_tradie(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id, client_id=current_user.id).first()

    if not service_request:
        return jsonify({
            'status': 'error',
            'message': 'Service request not found',
            'redirect_url': '/user/dashboard'
        }), 404

    if service_request.status != 'open':
        return jsonify({
            'status': 'error',
            'message': 'Service request is not open',
            'redirect_url': '/user/dashboard'
        }), 400

    tradie_id = request.form.get('tradie_id')
    if not tradie_id:
        return jsonify({
            'status': 'error',
            'message': 'Tradie ID is required',
            'redirect_url': '/user/dashboard'
        }), 400

    tradie = User.query.get(tradie_id)
    if not tradie:
        return jsonify({
            'status': 'error',
            'message': 'Tradie not found',
            'redirect_url': '/user/dashboard'
        }), 404

    service_request.tradie_id = tradie.id
    service_request.status = 'booked'
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Tradie selected successfully',
        'redirect_url': '/user/dashboard'
    })


@user.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@roles_required('user')
def edit_profile():
    user = current_user
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.phone_number = request.form.get('phone_number')
        user.location = request.form.get('cities')
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
        })

    return jsonify({
        "user": user.as_dict(),
        "cities": cities
    })

@user.route('/tradie/<int:tradie_id>', methods=['GET', 'POST'])
@login_required
@roles_required('user')
def view_tradie(tradie_id):
    tradie = User.query.filter(User.id == tradie_id, User.roles.any(name='tradie')).first_or_404()
    if not tradie or not tradie.activated:
        return jsonify({'message': 'The selected tradie is currently unavailable.'}), 400
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        due_date = request.form.get('due_date')
        description = request.form.get('description')
        location = request.form.get('location')
        estimated_hours = request.form.get('estimated_hours')
        hourly_rate = float(request.form.get('hourly_rate'))

        if hourly_rate < tradie.hourly_rate:
            return jsonify({
                'status': 'error',
                'message': f'Offered rate is below the minimum: ₹ {tradie.hourly_rate}',
                'redirect_url': f'/tradie/{tradie_id}'
            })


        total_cost = hourly_rate * float(estimated_hours)

        new_request = ServiceRequest(
            client_id=current_user.id,
            service_id=service_id,
            due_date=datetime.strptime(due_date, '%Y-%m-%d'),
            description=description,
            location=location,
            estimated_hours=float(estimated_hours),
            total_cost=total_cost,
            status="open"
        )
        new_request.requested_tradies.append(tradie)
        db.session.add(new_request)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Request created successfully',
            'redirect_url': f'/tradie/{tradie_id}'
        })


    return jsonify({
        "tradie": tradie.as_dict(),
        "cities": cities,
        "showForm": True
    })

@user.route('/search', methods=['GET'])
@login_required
@roles_required('user')
def search():
    query = request.args.get('q', '').strip()
    filters = request.args.getlist('filter')

    if not query:
        return jsonify({"query": query, "locations": [], "services": [], "tradies": [], "filters": filters})

    words = query.split()
    locations, services, tradies = [], [], []

    if "location" in filters or not filters:
        locations = User.query.filter(
            User.roles.any(name='tradie'),
            db.or_(*[User.location.ilike(f"%{word}%") for word in words])).all()

    if "service" in filters or not filters:
        services = Service.query.filter(
            Service.activated,
            db.or_(*[Service.name.ilike(f"%{word}%") for word in words])
            ).all()

    if "tradie" in filters or not filters:
        tradies = User.query.filter(
            User.roles.any(name='tradie'),
            db.or_(*[db.or_(User.first_name.ilike(f"%{word}%"), User.last_name.ilike(f"%{word}%")) for word in words])
        ).all()

    return jsonify({
        "query": query,
        "locations": [l.as_dict() for l in locations],
        "services": [s.as_dict() for s in services],
        "tradies": [t.as_dict() for t in tradies],
        "filters": filters
    })

@user.route('/tradies/location/<string:location>')
@login_required
@roles_required('user')
def tradies_by_location(location):
    tradies = User.query.filter(User.roles.any(name='tradie'), User.location.ilike(location)).all()
    services = {}
    for tradie in tradies:
        for service in tradie.service_categories:
            services.setdefault(service.name, []).append(tradie)

    return jsonify({
        "location": location,
        "services": {svc: [t.as_dict() for t in tradies] for svc, tradies in services.items()}
    })

@user.route('/tradies/service/<int:service_id>')
@login_required
@roles_required('user')
def tradies_by_service(service_id):
    service = Service.query.get_or_404(service_id)
    tradies = User.query.filter(User.roles.any(name='tradie'), User.service_categories.any(id=service_id)).all()
    locations = {}
    for tradie in tradies:
        locations.setdefault(tradie.location, []).append(tradie)

    return jsonify({
        "service": service.as_dict(),
        "locations": {loc: [t.as_dict() for t in tradies] for loc, tradies in locations.items()}
    })

@user.route('/user/profile/')
@login_required
@roles_required('user')
def user_profile():
    return jsonify({
        "user": current_user.as_dict()
    })

#! REVIEW SYSTEM ---------------------
@user.route('/review/make/<int:request_id>', methods=['GET', 'POST'])
@login_required
@roles_required('user')
def make_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        review_text = request.form.get('review')

        service_request.rating = rating
        service_request.review = review_text
        service_request.review_date = datetime.utcnow()

        db.session.commit()

        return jsonify({"status": "success"})

    return jsonify({
        "request": service_request.as_dict(),
        "tradie": service_request.professional.as_dict()
    })


@user.route('/review/user_view/<int:request_id>', methods=['GET'])
@login_required
@roles_required('user')
def view_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)

    return jsonify({
        "request": service_request.as_dict(),
        "tradie": service_request.professional.as_dict()
    })
