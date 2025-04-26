"""
cd "D:\C\Desktop\IITM\Diploma\MAD 2 Project\Household Services App\household_services_app_working"

flask --debug run

celery -A tradie_match.celery_worker worker --loglevel=info --pool=solo

celery -A tradie_match.celery_worker beat --loglevel=info

# `--pool=solo` avoids Celery's multithreading issues in Windows. 
# `beat` runs scheduled jobs
# `worker` runs the Celery tasks

$env:FLASK_APP="household_services_app.py"

cd '/mnt/d/C/Desktop/IITM/Diploma/MAD 2 Project/Household Services App/household_services_app_working'
"""

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app , db #, cli
from app.models import *

flask_app, celery_worker = create_app()

import app.celery_tasks
from celery.schedules import crontab

celery_worker.conf.beat_schedule = {
    # 'check-due-services-everyday-4pm': {
    #     'task': 'app.celery_tasks.check_due_services',
    #     # 'schedule': crontab(hour=16, minute=0),
    #     'schedule': crontab(minute='*/2'),
    # },
    'send-daily-tradie-requests-emails': {
        'task': 'app.celery_tasks.send_daily_tradie_requests_emails',
        # 'schedule': crontab(hour=10, minute=0),
        'schedule': crontab(minute='*/2'),
    },
    'send-daily-tradie-analytics-emails': {
        'task': 'app.celery_tasks.send_daily_tradie_analytics_emails',
        # 'schedule': crontab(hour=9, minute=0),
        'schedule': crontab(minute='*/2'),
    },
    'send-monthly-user-reports': {
        'task': 'app.celery_tasks.send_monthly_user_reports',
        # 'schedule': crontab(minute=0, hour=9, day_of_month=1),
        'schedule': crontab(minute='*/2'),
    }
    
}

@flask_app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 
            'user':User , 'service': Service, 'role':Role,
            'roles_users':roles_users, 'services_tradies':services_tradies,
            'celwork':celery_worker, 'serviceRequest':ServiceRequest,
            }

if __name__=="__main__":
    flask_app.run(debug=True)