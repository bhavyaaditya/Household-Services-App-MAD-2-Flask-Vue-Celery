from flask import Blueprint

tradie = Blueprint('tradie', __name__)

from app.tradie import routes

