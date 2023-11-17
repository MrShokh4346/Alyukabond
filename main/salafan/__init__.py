from flask import Blueprint

bp = Blueprint("salafan",  __name__)

from main.salafan import views
