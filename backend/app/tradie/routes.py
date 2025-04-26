from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template, abort
from flask_security import login_required, roles_required, roles_accepted, current_user
from app.models import db, User, ServiceRequest, Service
from datetime import datetime
from app.tradie import tradie
from sqlalchemy.sql import func
from datetime import timedelta
from app.cache import cache

@tradie.route('/tradie/dashboard', methods=['GET'])
@login_required
@roles_required('tradie')
def tradie_dashboard():
    if not current_user.is_authenticated:
        return jsonify({'redirect': url_for("auth.login")})

    applied_service_requests = current_user.applied_requests.all()
    applied_service_requests_ids = [req.id for req in applied_service_requests]

    requested_requests = ServiceRequest.query.filter(
        ServiceRequest.requested_tradies.any(id=current_user.id),
        ServiceRequest.status == 'open'
    ).all()

    available_service_requests = ServiceRequest.query.filter(
        ServiceRequest.status == 'open',
        ~ServiceRequest.requested_tradies.any(id=current_user.id),
        ServiceRequest.service_id.in_([s.id for s in current_user.service_categories])
    ).all()

    booked_requests = ServiceRequest.query.filter_by(tradie_id=current_user.id, status='booked').all()
    print(booked_requests)
    completed_requests = ServiceRequest.query.filter_by(tradie_id=current_user.id, status='completed').all()

    service_name = current_user.service_categories[0].name if current_user.service_categories else ''
    needs_service_selection = (
        len(current_user.service_categories) == 0 or
        not current_user.service_categories[0].activated
    )


    return jsonify({
        'requested_requests': [r.as_dict() for r in requested_requests],
        'available_service_requests': [r.as_dict() for r in available_service_requests],
        'applied_service_requests': [r.as_dict() for r in applied_service_requests],
        'applied_service_requests_ids': applied_service_requests_ids,
        'service_name': service_name,
        'needs_service_selection': needs_service_selection, # Flag for service delete funcitonality
        'booked_requests': [r.as_dict() for r in booked_requests],
        'completed_requests': [r.as_dict() for r in completed_requests],
        'tradie': current_user.as_dict()
    })

@tradie.route('/apply_request', methods=['POST'])
@login_required
@roles_required('tradie')
def apply_request():
    if not current_user.activated:
        return jsonify({'message': 'Your account is deactivated. You cannot apply to service requests.'}), 403
    request_id = request.form.get('request_id') or request.json.get('request_id')
    service_request = ServiceRequest.query.get(request_id)

    if not service_request:
        return jsonify({'status': 'error', 'message': 'Service request not found'}), 404

    if current_user.id in [tradie.id for tradie in service_request.applied_tradies]:
        return jsonify({'status': 'error', 'message': 'Already applied'}), 400

    service_request.applied_tradies.append(current_user)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Application successful'})

@tradie.route('/tradie/complete_service/<int:request_id>', methods=['POST'])
@login_required
@roles_required('tradie')
def complete_service(request_id):
    service_request = ServiceRequest.query.filter_by(id=request_id, tradie_id=current_user.id).first_or_404()

    if service_request.status != 'booked':
        return jsonify({'status': 'error', 'message': 'Only booked services can be completed'}), 400

    service_request.status = 'completed'
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Service request marked as completed'})

@tradie.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@roles_required('tradie')
def edit_profile():
    if request.method == 'POST':
        data = request.form or request.json
        tradie = current_user

        tradie.first_name = data.get('first_name')
        tradie.last_name = data.get('last_name')
        tradie.email = data.get('email')
        tradie.phone_number = data.get('phone_number')
        tradie.location = data.get('location')
        tradie.hourly_rate = float(data.get('hourly_rate', 0))
        tradie.years_of_experience = int(data.get('years_of_experience', 0))
        tradie.is_available = data.get('is_available') in ['true', 'True', True]

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'})

    tradie = current_user
    return jsonify({'tradie': tradie.as_dict()})

@tradie.route('/tradie/profile/')
@login_required
@roles_required('tradie')
def tradie_profile():
    return jsonify({
        "tradie": current_user.as_dict(),
        "activated": current_user.activated,
    })

@tradie.route('/review/tradie_view/<int:request_id>', methods=['GET'])
@login_required
@roles_required('tradie')
def tradie_view_review(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.tradie_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({
        "request": service_request.as_dict(),
        "user": service_request.client.as_dict()
    })


#! ANALYTICS ----------------------------
from collections import defaultdict
from datetime import datetime, timedelta
import calendar

@tradie.route('/tradie/analytics')
@login_required
@roles_accepted('tradie','admin')
@cache.memoize(timeout=90)
def tradie_analytics():
    if 'tradie' not in [role.name for role in current_user.roles]:
        abort(403)

    completed_services = ServiceRequest.query.filter_by(tradie_id=current_user.id, status='completed').all()

    total_revenue = sum(req.total_cost for req in completed_services)
    total_services = len(completed_services)

    # Location data
    location_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        location_summary[s.location]['services'] += 1
        location_summary[s.location]['revenue'] += s.total_cost
    location_data = [(loc, info['services'], info['revenue']) for loc, info in location_summary.items()]

    # Week-wise data
    week_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        created = s.created_date.date()
        start = created - timedelta(days=created.weekday())
        end = start + timedelta(days=6)
        label = f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"
        week_summary[label]['services'] += 1
        week_summary[label]['revenue'] += s.total_cost
    week_data = [{'label': label, 'services': v['services'], 'revenue': v['revenue']} for label, v in sorted(week_summary.items())]

    # Month-wise data
    month_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        created = s.created_date
        label = created.strftime('%b %Y')
        month_summary[label]['services'] += 1
        month_summary[label]['revenue'] += s.total_cost
    month_data = [{'label': label, 'services': v['services'], 'revenue': v['revenue']} for label, v in sorted(month_summary.items())]

    return jsonify({
        "total_revenue": total_revenue,
        "total_services": total_services,
        "location_data": location_data,
        "week_data": week_data,
        "month_data": month_data,
        "completed_services": [
            {
                "id": s.id,
                "rating": s.rating,
                "review": s.review,
                "review_date": s.review_date.strftime('%Y-%m-%d') if s.review_date else None,
                "category": {
                    "name": s.category.name if s.category else "N/A"
                }
            }
            for s in completed_services
        ]
    })

