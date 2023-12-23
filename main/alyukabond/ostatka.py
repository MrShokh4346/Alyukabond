from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.serializers import *
from flask import jsonify, request
from .utils import *
from .balance import *


# sklad
@bp.route('/warehouse/<string:name>')
@jwt_required()
def warehouse(name):
    turi = request.args.get('type')
    color = request.args.get("color")
    sort = request.args.get("sort")
    color1 = request.args.get("color1")
    color2 = request.args.get("color2")
    thkn = request.args.get("thickness")
    length = request.args.get("length")
    data = {
        'aluminy':filter_amount(name="aluminy_amount", thickness=thkn, color1=color) if name=='aluminy' else '',
        'sticker':filter_amount(name="sticker_amount", type=turi) if name=='sticker' else '',
        'glue':filter_amount(name="glue_amount") if name=='glue' else '',
        'alyukabond':filter_amount(name="alyukabond_amount", thickness=thkn, sort=sort, length=length, color1=color1, color2=color2) if name=='alyukabond' else ''
    }.get(name)
    # data = {}
    # alyukabond_amount = AlyukabondAmount.query.all()
    # alyuminy_amount = AluminyAmount.query.all()
    # glue_amount = GlueAmount.query.all()
    # sticker_amount = StickerAmount.query.all()
    # data["aluminy"] = al_amount_schema.dump(alyuminy_amount)
    # data["glue"] = glue_amount_schemas.dump(glue_amount)
    # data["sticker"] = sticker_amount_schemas.dump(sticker_amount)
    # data["alyukabond"] = alyukabond_amount_schema.dump(alyukabond_amount)
    return jsonify(data)

