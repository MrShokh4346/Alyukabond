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
    color1 = request.args.get("color1")
    color2 = request.args.get("color2")
    thkn = request.args.get("thickness")
    from_d = request.args.get('from')
    to_d = request.args.get('to')
    data = {
        'aluminy':filter_amount(name="aluminy_amount", thickness=thkn, color1=color, from_d=from_d, to_d=to_d),
        'sticker':filter_amount(name="sticker_amount", type=turi, from_d=from_d, to_d=to_d),
        'glue':filter_amount(name="glue_amount", from_d=from_d, to_d=to_d),
        'alyukabond':filter_amount(name="alyukabond_amount", thickness=thkn, color1=color1, color2=color2, from_d=from_d, to_d=to_d)
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

