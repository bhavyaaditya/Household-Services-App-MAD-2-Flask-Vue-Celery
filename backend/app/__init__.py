from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

from flask_security import Security,SQLAlchemyUserDatastore

from celery import Celery
from flask_cors import CORS
from flask_mail import Mail
from .cache import cache

# db = SQLAlchemy()
from .models import *

migrate = Migrate()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.url_map.strict_slashes = False  # This will treat '/login' and '/login/' as the same URL. There was some problem in Vue LoginForm which was solved by adding a trailing slash in the fetch URL. With this line, trailing slash or not, both will be treated as same.
    CORS(app, supports_credentials=True)    # `support_credentials=True` will enable flask_security login to work with CORS
    app.config.from_object(Config)
    # print(app.config['broker_url'])
    # print(app.config['result_backend'])

    app.app_context().push()
    # db.init_app(app=app)
    # db.create_all()
    
    mail.init_app(app)

    celery = Celery(
        app.import_name,
        broker="redis://172.31.240.158:6379/0",     # app.config['broker_url'],     # app.config['CELERY_BROKER_URL'],
        backend="redis://172.31.240.158:6379/0"    # app.config['result_backend']    # app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.broker_url = app.config['CELERY_BROKER_URL']
    celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']

    # celery.conf.update(app.config)
    # Wrap Celery tasks with Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    app.app_context().push()

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    init_db(app)
    migrate.init_app(app, db)

    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp)

    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp)

    from app.user import user as user_bp
    app.register_blueprint(user_bp)

    from app.tradie import tradie as tradie_bp
    app.register_blueprint(tradie_bp)

    # from app import routes

    # from .celery_tasks import generate_service_requests_csv

    cache.init_app(app, config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': app.config['REDIS_URL'],  # 'redis://172.31.240.158:6379'
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    app.app_context().push()

    print("\n" + "-"*40)
    print("Celery Configuration")
    print("Broker URL:", celery.conf.broker_url)
    print("Backend:", celery.conf.result_backend)
    print("-"*40 + "\n")

    return app, celery

