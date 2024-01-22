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
        rang = data.get('name').upper()
        cr = Color.query.all()
        for c in cr:
            if c.name == rang:
                return jsonify({"msg":"Этот цвет уже существует"})
        color = Color(name=rang)
        db.session.add(color)
        db.session.commit()
        return jsonify(msg="Success")
    else:
        color = Color.query.get(id)
        db.session.delete(color)
        db.session.commit()
        return jsonify(msg="Success")


# @bp.route('/add-balance-user', methods=['GET', 'POST'])
# @jwt_required()
# def add_balance_user():
#     if request.method=='GET':
#         users = AddBalanceUser.query.all()
#         return jsonify(add_balance_users_schema.dump(users))
#     else:
#         data = request.get_json()
#         user = AddBalanceUser(name=data.get('name'))
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(msg="Success")


@bp.route('/exchange-rate', methods=['GET', 'POST'])
@jwt_required()
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
        if color or thkn or (from_d and to_d):
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
            db.session.flush()
            for obj in data.get("aluminy"):
                # add_aluminy_amount(thickness=obj.get('thickness'), width=obj.get('list_width', 1.22),
                    # color_id=obj.get('color_id'), length=obj.get('list_length'), roll_weight=obj.get('roll_weight'), quantity=obj.get('quantity'))
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
                    date = nakladnoy.date,
                    provider = nakladnoy.provider
                )
                db.session.add(material)
            balance_minus(data.get("payed_price_d"))
            db.session.commit()
            return jsonify(msg="Success"), 201
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        id = request.args.get('material_id')
        if user.role in ['a']:
            material = Aluminy.query.get(id)
            if material.editable == True:
                data = request.get_json()
                try:
                    # surface = update_aluminy_amount(material=material, thickness=data.get('thickness', material.thickness), color=data.get('color_id', material.color_id),
                    #     list_length=data.get('list_length', material.list_length), list_width=data.get('list_width', material.list_width),
                    #     roll_weight=data.get('roll_weight', material.roll_weight), quantity=data.get('quantity', material.quantity))
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
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get("material_id")
            nakladnoy = db.get_or_404(AluminyNakladnoy, id)
            if nakladnoy.editable == True:
                balance_add(nakladnoy.payed_price_d)
                aluminies = Aluminy.query.filter_by(nakladnoy_id=nakladnoy.id).all()
                db.session.delete(nakladnoy)
                for aluminy in aluminies:
                    db.session.delete(aluminy)
                    db.session.commit()
                return jsonify(msg="Deleted")
            return  jsonify(msg="Неотредактируемый объект"), 400
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
        materials = Glue.query.order_by(Glue.date.desc()).all()
        return jsonify(glue_schemas.dump(materials))
    elif request.method == 'POST':
        try:
            data = request.get_json()
            # add_glue_amount(thickness=data.get("thickness"), width=data.get("width", 1.22), length=data.get("length"), roll_weight=data.get("weight"), quantity=data.get("quantity"))
            weight = data['weight']
            del data['weight']
            surface = data.get('width') * data.get('length') * data.get('quantity')
            material = Glue(**data, weight=weight * 1000, surface=surface)
            db.session.add(material)
            balance_minus(data.get("payed_price_d"))
            db.session.commit()
            return jsonify(msg="Success"), 201
        except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a']:
            material = Glue.query.get(id)
            if material.editable == True:
                try:
                    data = request.get_json()
                    weight = float(data.get("weight")) * 1000 if data.get("weight") else material.weight
                    extra_sum = data.get('total_price_d', material.total_price_d) - material.total_price_d
                    del data['weight']
                    # update_glue_amount(material=material, thickness=data.get('thickness', material.thickness), length=data.get('length', material.length),
                    #     width=data.get('width', material.width), roll_weight=weight, quantity=data.get('quantity', material.quantity))
                    material.thickness = data.get('thickness', material.thickness)
                    material.width = data.get('width', material.width)
                    material.length = data.get('length', material.length)
                    material.quantity = data.get('quantity', material.quantity)
                    material.weight = weight
                    material.surface = float(material.width) * float(material.length) * float(material.quantity)
                    material.price_per_kg = data.get('price_per_kg', material.price_per_kg)
                    material.total_price_d = data.get('total_price_d', material.total_price_d)
                    material.total_price_s = data.get('total_price_s', material.total_price_s)
                    material.payed_price_d = material.payed_price_d
                    material.payed_price_s = material.payed_price_s
                    material.debt_d = material.total_price_d - material.payed_price_d
                    material.debt_s = material.total_price_s - material.payed_price_s
                    material.provider = data.get('provider', material.provider)
                    db.session.commit()
                    balance_add(extra_sum)
                    return jsonify(msg='Success')
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Glue, id)
            if material.editable == True:
                balance_add(material.payed_price_d)
                db.session.delete(material)
                db.session.commit()
                return jsonify(msg="Deleted")
            return  jsonify(msg="Неотредактируемый объект"), 400
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
        materials = Sticker.query.order_by(Sticker.date.desc()).all()
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
            db.session.flush()
            for obj in data.get("sticker"):
                # surface = add_sticker_amount(width=obj.get('width', 1.22),  type=obj.get('type_sticker'), length=obj.get('length'), quantity=obj.get('quantity'))
                material = Sticker(
                    type_sticker = obj.get('type_sticker'),
                    width = obj.get('width'),
                    quantity = obj.get('quantity'),
                    length = obj.get('length'),
                    surface = float(obj.get('length')) * float(obj.get('width')) * float(obj.get('quantity')),
                    price_per_surface = obj.get('price_per_surface'),
                    price = obj.get('price'),
                    partiya = nakladnoy.partiya,
                    nakladnoy_id = nakladnoy.id,
                    date=nakladnoy.date,
                    provider = nakladnoy.provider
                )
                db.session.add(material)
            balance_minus(data.get("payed_price_d"))
            db.session.commit()
            return jsonify(msg="Success"), 201
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a']:
            data = request.get_json()
            material_id = request.args.get("material_id")
            material = Sticker.query.get(material_id)
            if material.editable == True:
                try:
                    # surface = update_sticker_amount(material=material,type=data.get('type_sticker', material.type_sticker), length=data.get('length', material.length), width=data.get('width', material.width),  quantity=data.get('quantity', material.quantity))
                    material.type_sticker = data.get('type_sticker', material.type_sticker)
                    material.width = data.get('width', material.width)
                    material.length = data.get('length', material.length)
                    material.price_per_surface = data.get('price_per_surface', material.price_per_surface)
                    material.quantity = data.get('quantity', material.quantity)
                    material.surface = float(material.width) * float(material.length) * float(material.quantity)
                    db.session.commit()
                    return jsonify(msg='Success')
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get("material_id")
            nakladnoy = db.get_or_404(StickerNakladnoy, id)
            if nakladnoy.editable == True:
                balance_add(nakladnoy.payed_price_d)
                stickers = Sticker.query.filter_by(nakladnoy_id=nakladnoy.id).all()
                db.session.delete(nakladnoy)
                for sticker in stickers:
                    db.session.delete(sticker)
                    db.session.commit()
                return jsonify(msg="Deleted")
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401


@bp.route('/makaron', methods=['GET','POST', 'DELETE'])
def makaron():
    if request.method == 'GET':
        makaron = Makaron.query.order_by(Makaron.date.desc()).all()
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


@bp.route('/granula-otxod', methods=['GET','POST', 'DELETE'])
def granula_otxod():
    if request.method == 'GET':
        makaron = GranulaOtxod.query.order_by(GranulaOtxod.date.desc()).all()
        return jsonify(granula_otxod_schema.dump(makaron))
    elif request.method == 'POST':
        data = request.get_json()
        makaron = GranulaOtxod(
            weight = data.get('weight')
        )
        granula = GranulaAmount.query.filter_by(sklad=False).first()
        granula.weight -= makaron.weight
        db.session.add(makaron)
        db.session.commit()
        return jsonify(msg="Created")
    else:
        id = request.args.get('makaron_id')
        makaron = db.get_or_404(GranulaOtxod, id)
        db.session.delete(makaron)
        db.session.commit()
        return jsonify(msg="Success")
