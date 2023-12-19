from flask import Blueprint

bp = Blueprint("alyukabond",  __name__)

from main.alyukabond import prixod
from main.alyukabond import proizvodeno
from main.alyukabond import prodano
from main.alyukabond import ostatka
from main.alyukabond import otchot


