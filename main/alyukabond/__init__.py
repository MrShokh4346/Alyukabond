from flask import Blueprint

bp = Blueprint("alyukabond",  __name__)

from main.alyukabond import views
