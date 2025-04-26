from flask import Blueprint, request, jsonify, send_file, make_response, Response, render_template
from flask_security import login_required, roles_required, current_user
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.models import db, User, Role, Service, ServiceRequest, roles_users
import pandas as pd
from app.admin import admin

from collections import defaultdict
from markupsafe import Markup

from app.cache import cache
import io
from xhtml2pdf import pisa

# -------------------- Admin Dashboard --------------------
@admin.route('/admin/dashboard', methods=['GET'])
@roles_required('admin')
def admin_dashboard():
    tradies = User.query.join(roles_users).join(Role).filter(Role.name == 'tradie').all()
    users = User.query.join(roles_users).join(Role).filter(Role.name == 'user').all()
    services = Service.query.filter_by(activated=True).all()

    return jsonify({
        "tradies": [t.as_dict() for t in tradies],
        "users": [u.as_dict() for u in users],
        "services": [s.as_dict() for s in services]
    })


# -------------------- Update Tradie/User/Service --------------------
@admin.route('/update_tradie_activated', methods=['POST'])
@login_required
@roles_required('admin')
def update_tradie_activated():
    data = request.get_json()
    tradie = User.query.get(data.get("tradie_id"))
    if tradie:
        tradie.activated = data.get("activated")
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Tradie not found"}), 404

@admin.route('/update_user_activated', methods=['POST'])
@login_required
@roles_required('admin')
def update_user_activated():
    data = request.get_json()
    user = User.query.get(data.get("user_id"))
    if user:
        user.activated = data.get("activated")
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "User not found"}), 404

@admin.route('/update_service', methods=['POST'])
@login_required
@roles_required('admin')
def update_service():
    data = request.get_json()
    service = Service.query.get(data.get("id"))
    if service:
        service.name = data.get("name")
        service.description = data.get("description")
        service.base_price = data.get("base_price", 1)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Service not found"}), 404

@admin.route('/add_service', methods=['POST'])
@login_required
@roles_required('admin')
def add_service():
    data = request.get_json()
    if not data.get("name") or not data.get("description"):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    if Service.query.filter_by(name=data["name"]).first():
        return jsonify({"status": "error", "message": "Service already exists"}), 400

    new_service = Service(
        name=data["name"],
        description=data["description"],
        base_price=data.get("base_price", 1)
    )
    db.session.add(new_service)
    db.session.commit()
    return jsonify({"status": "success"})

@admin.route('/delete_service', methods=['POST'])
@login_required
@roles_required('admin')
def delete_service():
    data = request.get_json()
    service_id = data.get('service_id')
    service = Service.query.get(service_id)

    if not service:
        return jsonify({"status": "error", "message": "Service not found"}), 404

    # Soft delete
    service.activated = False

    # Delete only open service requests of this service
    ServiceRequest.query.filter_by(service_id=service_id, status='open').delete()

    # Remove service from corresponding tradies
    tradies = service.professionals.all()
    for tradie in tradies:
        tradie.service_categories.clear()  

    db.session.commit()
    return jsonify({"status": "success"})




# -------------------- Admin Analytics --------------------
@admin.route('/admin/analytics')
@login_required
@roles_required('admin')
@cache.memoize(timeout=90)
def admin_analytics():

    completed_services = ServiceRequest.query.filter_by(status='completed').all()

    total_revenue = sum(s.total_cost for s in completed_services)
    total_services = len(completed_services)

    # Location summary
    location_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        location_summary[s.location]['services'] += 1
        location_summary[s.location]['revenue'] += s.total_cost
    location_data = [(k, v['services'], v['revenue']) for k, v in location_summary.items()]

    # Weekly summary
    week_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        dt = s.created_date.date()
        week_start = dt - timedelta(days=dt.weekday())
        week_end = week_start + timedelta(days=6)
        label = f"{week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}"
        week_summary[label]['services'] += 1
        week_summary[label]['revenue'] += s.total_cost
    week_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(week_summary.items())]

    # Monthly summary
    month_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        label = s.created_date.strftime('%b %Y')
        month_summary[label]['services'] += 1
        month_summary[label]['revenue'] += s.total_cost
    month_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(month_summary.items())]

    return jsonify({
        'total_revenue': total_revenue,
        'total_services': total_services,
        'location_data': location_data,
        'week_data': week_data,
        'month_data': month_data
    })


# -------------------- Tradie Analytics (Admin View) --------------------
@admin.route('/admin/tradie/<int:tradie_id>/analytics')
@login_required
@roles_required('admin')
def admin_view_tradie_analytics(tradie_id):
    from collections import defaultdict
    from datetime import timedelta
    from flask import jsonify

    tradie = User.query.get_or_404(tradie_id)
    completed_services = ServiceRequest.query.filter_by(tradie_id=tradie.id, status='completed').all()

    total_revenue = sum(s.total_cost for s in completed_services)
    total_services = len(completed_services)

    # Location summary
    location_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        location_summary[s.location]['services'] += 1
        location_summary[s.location]['revenue'] += s.total_cost
    location_data = [(k, v['services'], v['revenue']) for k, v in location_summary.items()]

    # Weekly summary
    week_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        dt = s.created_date.date()
        week_start = dt - timedelta(days=dt.weekday())
        week_end = week_start + timedelta(days=6)
        label = f"{week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}"
        week_summary[label]['services'] += 1
        week_summary[label]['revenue'] += s.total_cost
    week_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(week_summary.items())]

    # Monthly summary
    month_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        label = s.created_date.strftime('%b %Y')
        month_summary[label]['services'] += 1
        month_summary[label]['revenue'] += s.total_cost
    month_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(month_summary.items())]

    # Reviews
    reviews = [{
        'id': s.id,
        'service_name': s.category.name if s.category else 'N/A',
        'rating': s.rating,
        'review': s.review,
        'review_date': s.review_date.strftime('%Y-%m-%d') if s.review_date else None
    } for s in completed_services if s.rating]

    average_rating = round(sum(s['rating'] for s in reviews) / len(reviews), 2) if reviews else None

    return jsonify({
        'tradie': tradie.as_dict(),
        'total_revenue': total_revenue,
        'total_services': total_services,
        'average_rating': average_rating,
        'location_data': location_data,
        'reviews': reviews,
        'week_data': week_data,
        'month_data': month_data
    })



# -------------------- Celery Download Routes --------------------
from app.celery_tasks import generate_service_requests_csv

@admin.route('/admin/download/service_requests', methods=['POST'])
@login_required
@roles_required('admin')
def start_csv_download():
    task = generate_service_requests_csv.apply_async()
    return jsonify({"task_id": task.id, "message": "CSV generation started"}), 202

@admin.route('/admin/download/service_requests/status/<task_id>')
@login_required
@roles_required('admin')
def check_csv_status(task_id):
    task = generate_service_requests_csv.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({"status": "Pending"})
    elif task.state == 'SUCCESS':
        return jsonify({"status": "Completed", "file_path": task.result})
    elif task.state == 'FAILURE':
        return jsonify({"status": "Failed"})
    return jsonify({"status": "Processing"})

@admin.route('/admin/download/service_requests/file')
@login_required
@roles_required('admin')
def download_csv():
    return send_file("exports/service_requests.csv", as_attachment=True)

#! NON CELERY VERSION OF DOWNLOADS ---------------------------
@admin.route('/admin/download/admin_analytics/pdf')
@login_required
@roles_required('admin')
def download_admin_analytics_pdf():
    # Fetch all completed services
    completed_services = ServiceRequest.query.filter_by(status='completed').all()

    # Total revenue and service count
    total_revenue = sum(s.total_cost for s in completed_services)
    total_services = len(completed_services)

    # Location-wise summary
    location_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        location_summary[s.location]['services'] += 1
        location_summary[s.location]['revenue'] += s.total_cost
    location_data = [(k, v['services'], v['revenue']) for k, v in location_summary.items()]

    # Week-wise summary
    week_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        dt = s.created_date.date()
        week_start = dt - timedelta(days=dt.weekday())
        week_end = week_start + timedelta(days=6)
        label = f"{week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}"
        week_summary[label]['services'] += 1
        week_summary[label]['revenue'] += s.total_cost
    week_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(week_summary.items())]

    # Month-wise summary
    month_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
    for s in completed_services:
        label = s.created_date.strftime('%b %Y')
        month_summary[label]['services'] += 1
        month_summary[label]['revenue'] += s.total_cost
    month_data = [{'label': k, 'services': v['services'], 'revenue': v['revenue']} for k, v in sorted(month_summary.items())]

    # Render to HTML
    html = render_template(
        "admin_analytics_pdf.html",
        total_revenue=total_revenue,
        total_services=total_services,
        location_data=location_data,
        week_data=week_data,
        month_data=month_data
    )

    # Convert HTML to PDF
    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=admin_analytics.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response


@admin.route('/download/service_requests/csv', methods=['GET'])
@login_required
@roles_required('admin')
def download_service_requests_csv():
    # Fetch all service requests
    service_requests = ServiceRequest.query.all()

    # Build a list of dictionaries for DataFrame
    data = []
    for req in service_requests:
        data.append({
            "ID": req.id,
            "Client": f"{req.client.first_name} {req.client.last_name}" if req.client else "N/A",
            "Tradie": f"{req.professional.first_name} {req.professional.last_name}" if req.professional else "N/A",
            "Service": req.category.name if req.category else "N/A",
            "Location": req.location,
            "Description": req.description,
            "Status": req.status,
            "Created Date": req.created_date.strftime('%Y-%m-%d') if req.created_date else "N/A",
            "Due Date": req.due_date.strftime('%Y-%m-%d') if req.due_date else "N/A",
            "Total Cost": req.total_cost
        })

    # Create DataFrame and convert to CSV
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)

    # Return CSV as downloadable response
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=service_requests.csv"}
    )
