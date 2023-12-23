from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import  get_jwt_identity, jwt_required
from main.serializers import *
from flask import  jsonify, request
from .utils import *
from .balance import *


@bp.route('/color', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def color():
    id = request.args.get('color_id')
    if request.method == 'GET':
        if id is not None:
            color = Color.query.get(id)
            return jsonify(color_schema.dump(color))
        colors = Color.query.all()
        return jsonify(colors_schema.dump(colors))
    elif request.method == 'POST':
        data = request.get_json()
        color = Color(name=data.get('name'))
        db.session.add(color)
        db.session.commit()
        return jsonify(msg="Success")
    else:
        color = Color.query.get(id)
        db.session.delete(color)
        db.session.commit()
        return jsonify(msg="Success")
    

# @bp.route('/aluminy-thickness', methods=['GET', 'POST', 'DELETE'])
# @jwt_required()
# def aluminy_thickness():
#     id = request.args.get('id')
#     if request.method == 'GET':
#         if id is not None:
#             thkn = AluminyThickness.query.get(id)
#             return jsonify(aluminy_thickness_schema.dump(thkn))
#         thkns = AluminyThickness.query.all()
#         return jsonify(aluminy_thickness_schemas.dump(thkns))
#     elif request.method == 'POST':
#         data = request.get_json()
#         thkn = AluminyThickness(thickness=data.get('thickness'))
#         db.session.add(thkn)
#         db.session.commit()
#         return jsonify(msg="Success")
#     else:
#         thkn = AluminyThickness.query.get(id)
#         db.session.delete(thkn)
#         db.session.commit()
#         return jsonify(msg="Success")


# @bp.route('/alyukabond-length', methods=['GET', 'POST', 'DELETE'])
# @jwt_required()
# def alyukabond_length():
#     id = request.args.get('id')
#     if request.method == 'GET':
#         if id is not None:
#             thkn = AlyukabondLength.query.get(id)
#             return jsonify(alyukabond_length_schema.dump(thkn))
#         thkns = AlyukabondLength.query.all()
#         return jsonify(alyukabond_length_schemas.dump(thkns))
#     elif request.method == 'POST':
#         data = request.get_json()
#         thkn = AlyukabondLength(length=data.get('thickness'))
#         db.session.add(thkn)
#         db.session.commit()
#         return jsonify(msg="Success")
#     else:
#         thkn = AlyukabondLength.query.get(id)
#         db.session.delete(thkn)
#         db.session.commit()
#         return jsonify(msg="Success")


@bp.route('/exchange-rate', methods=['GET', 'POST'])
def exchange_rate():
    if request.method == 'GET':
        rate = ExchangeRate.query.order_by(ExchangeRate.id.desc()).first()
        return jsonify(exchange_rate_schema.dump(rate))
    else:
        data = request.get_json()
        rate = ExchangeRate(rate=data.get('rate'))
        db.session.add(rate)
        db.session.commit()
        return jsonify(msg='Success')


# aluminiy xomashyo malumot kiritish
@bp.route('/alyuminy-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def alyuminy_material():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        material_id = request.args.get("material_id")
        color = request.args.get("color_id")
        thkn = request.args.get("thickness")
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if color or thkn or from_d or to_d:
            data = filter_amount(name="aluminy", thickness=thkn, color1=color, from_d=from_d, to_d=to_d)
            return jsonify(data)
        elif material_id is not None:
            return jsonify(aluminy_schema.dump(Aluminy.query.get_or_404(material_id)))
        materials = Aluminy.query.order_by(Aluminy.date.desc()).all()
        return jsonify(aluminy_schemas.dump(materials))
    elif request.method == 'POST':
        data = request.get_json()
        try:
            nakladnoy = AluminyNakladnoy(
                partiya = data.get("partiya"),
                total_weight = data.get("total_weight"),
                total_price_d = data.get("total_price_d"),
                total_price_s = data.get("total_price_s"),
                payed_price_d = data.get("payed_price_d"),
                payed_price_s = data.get("payed_price_s"),
                debt_d = data.get("debt_d"),
                debt_s = data.get("debt_s"),
                provider = data.get("provider")
            )
            db.session.add(nakladnoy)
            for obj in data.get("aluminy"):
                add_aluminy_amount(thickness=obj.get('thickness'), width=obj.get('list_width', 1.22),
                    color_id=obj.get('color_id'), length=obj.get('list_length'), roll_weight=obj.get('roll_weight'), quantity=obj.get('quantity'))
                material = Aluminy(
                    color_id = obj.get('color_id'),
                    nakladnoy_id = nakladnoy.id,
                    thickness = obj.get('thickness'),
                    list_width = obj.get('list_width'),
                    list_length = obj.get('list_length'),
                    roll_weight = obj.get('roll_weight'),
                    price_per_kg = obj.get('price_per_kg'),
                    price = obj.get('price'),
                    quantity = obj.get('quantity'),
                    partiya = nakladnoy.partiya, 
                    date = nakladnoy.date
                )
                db.session.add(material)
            db.session.commit()
            balance_minus(data.get("payed_price_s"))
            return jsonify(msg="Success"), 201
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        id = request.args.get('material_id')
        if user.role in ['a', 'se']:
            data = request.get_json()
            try:
                material = Aluminy.query.get(id)
                surface = update_aluminy_amount(material=material, thickness=data.get('thickness', material.thickness), color=data.get('color_id', material.color_id),
                    list_length=data.get('list_length', material.list_length), list_width=data.get('list_width', material.list_width),
                    roll_weight=data.get('roll_weight', material.roll_weight), quantity=data.get('quantity', material.quantity))
                material.color_id = data.get('color_id', material.color_id)
                material.thickness = data.get('thickness', material.thickness)
                material.list_width = data.get('list_width', material.list_width)
                material.list_length = data.get('list_length', material.list_length)
                material.quantity = data.get('quantity', material.quantity)
                material.roll_weight = data.get('roll_weight', material.roll_weight)
                material.price_per_kg = data.get('price_per_kg', material.price_per_kg)
                db.session.commit()
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get("material_id")
            material = db.get_or_404(Aluminy, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# kley xomashyo malumot kiritish
@bp.route('/glue-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def glue_material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        material_id = request.args.get("material_id")
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        thkn = request.args.get("thickness")
        if from_d and to_d:
            data=filter_amount(name="glue", thickness=thkn, from_d=from_d, to_d=to_d) 
            return jsonify(data)
        if material_id is not None:
            return jsonify(glue_schema.dump(Glue.query.get_or_404(material_id)))
        materials = Glue.query.all()
        return jsonify(glue_schemas.dump(materials))
    elif request.method == 'POST':
        try:
            data = request.get_json()
            add_glue_amount(thickness=data.get("thickness"), width=data.get("width", 1.22), length=data.get("length"), roll_weight=data.get("weight"), quantity=data.get("quantity"))
            material = Glue(**data)
            db.session.add(material)
            db.session.commit()
            balance_minus(data.get("payed_price_s"))
            return jsonify(msg="Success"), 201
        except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            try:
                data = request.get_json()
                material = Glue.query.get(id)
                update_glue_amount(material=material, thickness=data.get('thickness', material.thickness), length=data.get('length', material.length),
                     width=data.get('width', material.width), roll_weight=data.get('weight', material.weight), quantity=data.get('quantity', material.quantity))
                material.thickness = data.get('thickness', material.thickness)
                material.width = data.get('width', material.width)
                material.length = data.get('length', material.length)
                material.quantity = data.get('quantity', material.quantity)
                material.weight = data.get('weight', material.weight)
                material.price_per_kg = data.get('price_per_kg', material.price_per_kg)
                material.provider = data.get('provider', material.provider)
                db.session.commit()
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Glue, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# nakleyka xomashyo malumot kiritish
@bp.route('/sticker-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def sticker_material():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        material_id = request.args.get("material_id")
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        typ = request.args.get("type")
        if typ or from_d  or to_d:
            data = filter_amount(name="sticker", type=typ, from_d=from_d, to_d=to_d)
            return jsonify(data)
        if material_id is not None:
            return jsonify(sticker_schema.dump(Sticker.query.get_or_404(material_id)))
        materials = Sticker.query.all()
        return jsonify(sticker_schemas.dump(materials))
    elif request.method == 'POST':
        try:
            data = request.get_json()
            nakladnoy = StickerNakladnoy(
                partiya = data.get("partiya"),
                total_price_d = data.get("total_price_d"),
                total_price_s = data.get("total_price_s"),
                payed_price_d = data.get("payed_price_d"),
                payed_price_s = data.get("payed_price_s"),
                debt_d = data.get("debt_d"),
                debt_s = data.get("debt_s"),
                provider = data.get("provider")
            )
            db.session.add(nakladnoy)
            for obj in data.get("sticker"):
                surface = add_sticker_amount(width=obj.get('width', 1.22),  type=obj.get('type_sticker'), length=obj.get('length'), quantity=obj.get('quantity'))
                material = Sticker(
                    type_sticker = obj.get('type_sticker'),
                    width = obj.get('width'),
                    quantity = obj.get('quantity'),
                    length = obj.get('length'),
                    surface = surface,
                    price_per_surface = obj.get('price_per_surface'),
                    price = obj.get('price'),
                    nakladnoy_id = nakladnoy.id,
                    date=nakladnoy.date
                )
                db.session.add(material)
            db.session.commit()
            balance_minus(data.get("payed_price_s"))
            return jsonify(msg="Success"), 201
        except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            data = request.get_json()
            try:
                material = Sticker.query.get(id)
                surface = update_sticker_amount(material=material,type=data.get('type_sticker', material.type_sticker), length=data.get('length', material.length), width=data.get('width', material.width),  quantity=data.get('quantity', material.quantity))
                material.type_sticker = data.get('type_sticker', material.type_sticker)
                material.width = data.get('width', material.width)
                material.length = data.get('length', material.length)
                material.quantity = data.get('quantity', material.quantity)
                material.surface += surface
                material.provider = data.get('provider', material.provider)
                db.session.commit()
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get("material_id")
            material = db.get_or_404(Sticker, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify(msg="У вас нет полномочий на это действие"), 401


@bp.route('/makaron', methods=['GET','POST', 'DELETE'])
def makaron():
    if request.method == 'GET':
        makaron = Makaron.query.all()
        return jsonify(makaron_schema.dump(makaron))
    elif request.method == 'POST':
        data = request.get_json()
        makaron = Makaron(
            color1 = data.get('color1'),
            color2 = data.get('color2'),
            al_thickness = data.get('thickness'),
            list_length = data.get('length'),
            weight = data.get('weight')
        )
        db.session.add(makaron)
        db.session.commit()
        return jsonify(msg="Created")
    else:
        id = request.args.get('makaron_id')
        makaron = db.get_or_404(Makaron, id)
        db.session.delete(makaron)
        db.session.commit()
        return jsonify(msg="Success")

