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
    color2 = 1 if turi == "1" else color2
    al_thkn = request.args.get("al_thickness")
    thkn = request.args.get("thickness")

    length = request.args.get("length")
    data = {
        'aluminy':filter_amount(name="aluminy_amount", thickness=thkn, color1=color) if name=='aluminy' else '',
        'sticker':filter_amount(name="sticker_amount", type=turi) if name=='sticker' else '',
        'glue':filter_amount(name="glue_amount") if name=='glue' else '',
        'alyukabond':filter_amount(name="alyukabond_amount", thickness=al_thkn, type=turi, sort=sort, length=length, color1=color1, color2=color2) if name=='alyukabond' else ''
    }.get(name)
    return jsonify(data)


# aluminy - color, thkn
# glue
# sticker - type
# salafan
# aluykabond - color1, color2, al_thkn 
@bp.route('/add-warehouse')
@jwt_required()
def add_warehouse():
    name = request.args.get("name")
    id = request.args.get("id")
    if name == "aluminy":
        nakladnoy = AluminyNakladnoy.query.get(id)
        if nakladnoy.editable == True:
            nakladnoy.editable=False
            db.session.commit()
            aluminies = Aluminy.query.filter_by(nakladnoy_id=nakladnoy.id).all()
            for aluminy in aluminies:
                aluminy.editable=False
                db.session.commit()
                q = AluminyAmount.query.filter_by(color_id=aluminy.color_id, thickness=aluminy.thickness).first()
                add_aluminy_amount(thickness=aluminy.thickness, width=aluminy.list_width, color_id=aluminy.color_id, length=aluminy.list_length, roll_weight=aluminy.roll_weight, quantity=aluminy.quantity)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "alyukabond":
        aluykabond = Alyukabond.query.get(id)
        if aluykabond.editable == True:
            aluykabond.editable=False
            db.session.commit()
            add_alyukabond_amount(type=aluykabond.type_sticker, type_product=aluykabond.type_product, color1=aluykabond.color1_id, color2=aluykabond.color2_id, sort=aluykabond.sort, length=aluykabond.list_length, al_thickness=aluykabond.al_thickness, product_thickness=aluykabond.product_thickness, quantity=aluykabond.quantity)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "sticker":
        nakladnoy = StickerNakladnoy.query.get(id)
        if nakladnoy.editable == True:
            nakladnoy.editable=False
            db.session.commit()
            stickers = Sticker.query.filter_by(nakladnoy_id=nakladnoy.id).all()
            for sticker in stickers:
                sticker.editable=False
                db.session.commit()
                add_sticker_amount(width=sticker.width,  type=sticker.type_sticker, length=sticker.length, quantity=sticker.quantity)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "glue":
        glue = Glue.query.get(id)
        if glue.editable == True:
            glue.editable=False
            db.session.commit()
            add_glue_amount(thickness=glue.thickness, width=glue.width, length=glue.length, roll_weight=glue.weight, quantity=glue.quantity)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "granula":
        granula = GranulaPoteriya.query.get(id)
        if granula.editable == True:
            granula.editable=False
            db.session.commit()
            add_granula_amount(granula_weight=granula.granula_weight)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "material":
        material = GranulaMaterial.query.get(id)
        if material.editable == True:
            material.editable=False
            db.session.commit()
            add_material_amount(material.weight)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "setka":
        setka = Setka.query.get(id)
        if setka.editable == True:
            setka.editable=False
            db.session.commit()
            add_material_amount(setka.bulk)
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")
    elif name == "sale":
        sale = SaledProduct.query.get(id)
        if sale.editable == True:
            sale.editable=False
            db.session.commit()
            return jsonify(msg="Success")
        return jsonify(msg="Вы не должны редактировать этот объект")