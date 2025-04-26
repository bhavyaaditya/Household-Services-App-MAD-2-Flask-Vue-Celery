import os

# from icecream import ic
# os.chdir("d:/C/Desktop/IITM/Diploma/MAD 2 Project/Household Services App/household_services_app_working/")
# ic(os.getcwd())

import pandas as pd
from celery import shared_task
from app import db, mail
from flask import current_app, render_template
from app.models import User, Role, ServiceRequest

from celery.schedules import crontab
from datetime import date, datetime, timedelta

from flask_mail import Message

from collections import defaultdict

EXPORT_FOLDER = "exports"

#! ADMIN TASKS ---------------------
@shared_task
def generate_service_requests_csv():

    # Ensure export folder exists
    if not os.path.exists(EXPORT_FOLDER):
        os.makedirs(EXPORT_FOLDER)

    # Fetch all service requests
    service_requests = ServiceRequest.query.all()

    # Prepare data
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
            "Created Date": req.created_date.strftime('%Y-%m-%d'),
            "Due Date": req.due_date.strftime('%Y-%m-%d') if req.due_date else "N/A",
            "Total Cost": req.total_cost
        })

    # Convert to DataFrame & Save CSV
    df = pd.DataFrame(data)
    file_path = os.path.join(EXPORT_FOLDER, "service_requests.csv")
    df.to_csv(file_path, index=False)

    return file_path  # Return file path for download

#! DUMMY TASKS ---------------------
@shared_task
def check_due_services():
    today = date.today()
    due_requests = ServiceRequest.query.filter(
        db.func.date(ServiceRequest.due_date) == today
    ).all()

    if due_requests:
        print(f"{len(due_requests)} service request(s) due today.")
        return len(due_requests)
    else:
        print("NO SERVICE TODAY")
        return "NO SERVICE TODAY"

#! TRADIE TASKS ---------------------
@shared_task
def send_daily_tradie_requests_emails():
    today = date.today()
    tradies = User.query.join(User.roles).filter_by(name='tradie').all()

    for tradie in tradies:
        open_requests = ServiceRequest.query.filter(
            ServiceRequest.status == 'open',
            ServiceRequest.location == tradie.location,
            ServiceRequest.service_id.in_([s.id for s in tradie.service_categories])
        ).all()

        due_requests = ServiceRequest.query.filter_by(
            tradie_id=tradie.id,
            due_date=today
        ).all()

        rejected_requests = [
            req for req in tradie.applied_requests
            if req.tradie_id and req.tradie_id != tradie.id
        ]

        accepted_requests = ServiceRequest.query.filter_by(
            tradie_id=tradie.id
        ).filter(ServiceRequest.created_date <= today).all()

        if not (open_requests or due_requests or rejected_requests or accepted_requests):
            continue

        html = render_template(
            'tradie_daily_update.html',
            tradie=tradie,
            today=today.strftime('%d %B %Y'),
            open_requests=open_requests,
            due_requests=due_requests,
            accepted_requests=accepted_requests,
            rejected_requests=rejected_requests
        )

        msg = Message(
            subject='Your Daily Service Updates',
            recipients=[tradie.email],
            html=html
        )
        mail.send(msg)

    return "Daily tradie emails sent"


@shared_task
def send_daily_tradie_analytics_emails():
    today = date.today()

    tradies = User.query.join(User.roles).filter(Role.name == 'tradie').all()

    for tradie in tradies:
        completed_services = ServiceRequest.query.filter_by(tradie_id=tradie.id, status='completed').all()

        total_revenue = sum(req.total_cost for req in completed_services)
        total_services = len(completed_services)

        # Location breakdown
        location_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
        for s in completed_services:
            location_summary[s.location]['services'] += 1
            location_summary[s.location]['revenue'] += s.total_cost
        location_data = [(loc, info['services'], info['revenue']) for loc, info in location_summary.items()]

        # Weekly grouping
        week_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
        for s in completed_services:
            created = s.created_date.date()
            start = created - timedelta(days=created.weekday())
            end = start + timedelta(days=6)
            label = f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"
            week_summary[label]['services'] += 1
            week_summary[label]['revenue'] += s.total_cost
        week_data = [{'label': label, 'services': v['services'], 'revenue': v['revenue']} for label, v in sorted(week_summary.items())]

        # Monthly grouping
        month_summary = defaultdict(lambda: {'services': 0, 'revenue': 0})
        for s in completed_services:
            created = s.created_date
            label = created.strftime('%b %Y')
            month_summary[label]['services'] += 1
            month_summary[label]['revenue'] += s.total_cost
        month_data = [{'label': label, 'services': v['services'], 'revenue': v['revenue']} for label, v in sorted(month_summary.items())]

        # Reviews
        reviews = []
        rated = [s for s in completed_services if s.rating]
        for s in rated:
            reviews.append({
                'service_name': s.category.name if s.category else 'N/A',
                'rating': s.rating,
                'review': s.review,
                'review_date': s.review_date.strftime('%Y-%m-%d') if s.review_date else None
            })

        html = render_template(
            'tradie_weekly_analytics_email.html',
            tradie=tradie,
            total_revenue=total_revenue,
            total_services=total_services,
            average_rating=round(sum(s['rating'] for s in reviews) / len(reviews), 2) if reviews else None,
            location_data=location_data,
            week_data=week_data,
            month_data=month_data,
            reviews=reviews
        )

        msg = Message(subject='Your Service Analytics',
                      recipients=[tradie.email],
                      html=html)
        mail.send(msg)

    return "Daily tradie analytics emails sent"

#! USER TASKS ---------------------
def get_monthly_user_data(user):
    today = datetime.utcnow()
    start_of_month = today.replace(day=1)

    requests = ServiceRequest.query.filter(
        ServiceRequest.client_id == user.id,
        ServiceRequest.created_date >= start_of_month
    ).all()

    total_requested = len(requests)
    total_completed = sum(1 for r in requests if r.status == 'completed')
    total_cancelled = sum(1 for r in requests if r.status == 'cancelled')
    total_spent = sum(r.total_cost for r in requests if r.status == 'completed')

    breakdown = {}
    for r in requests:
        if r.category:
            name = r.category.name
            breakdown[name] = breakdown.get(name, 0) + 1

    return {
        "total_requested": total_requested,
        "total_completed": total_completed,
        "total_cancelled": total_cancelled,
        "total_spent": total_spent,
        "breakdown_by_service": breakdown
    }

@shared_task
def send_monthly_user_reports():
    today = datetime.utcnow()
    month_year = today.strftime('%B %Y')

    users = User.query.join(User.roles).filter_by(name='user').all()

    for user in users:
        data = get_monthly_user_data(user)
        
        if data['total_requested'] == 0:
            continue

        html = render_template(
            'monthly_user_report.html',
            user=user,
            month_year=month_year,
            **data
        )

        msg = Message(
            subject=f"Your {month_year} Activity Summary",
            recipients=[user.email],
            html=html
        )
        mail.send(msg)

    return f"Monthly reports sent for {month_year}"
