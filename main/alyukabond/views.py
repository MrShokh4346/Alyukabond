from datetime import datetime, timedelta, timezone, date
from flask import Blueprint
from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from main.serializers import *
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import  send_from_directory, jsonify, request
from uuid import uuid1
from sqlalchemy.exc import SQLAlchemyError
import os
from openpyxl import Workbook, load_workbook
from sqlalchemy import text
import shutil
from .amounts import *
from .balance import *


@bp.route('/exchange-rate', methods=['GET', 'POST'])
def exchange_rate():
    if request.method == 'POST':
        data = request.get_json()
        rate = ExchangeRate(rate=data.get('rate'))
        db.session.add(rate)
        db.session.commit()
        return jsonify(msg='Success')
    else:
        rate = ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
        data = {"rate":rate.rate,  "date":f"{rate.date:%Y-%m-%d}" } if rate else None
        return jsonify(data)

@bp.route('/filter')
def filter_route():
    name =request.args.get("name")
    typ = request.args.get("type")
    color1 = request.args.get("color1")
    color2 = request.args.get("color2")

    thkn = request.args.get("thickness")
    data = filter_amount(name=name, type=typ, thickness=thkn, color1=color1, color2=color2)
    return jsonify(data)


# aluminiy xomashyo malumot kiritish
@bp.route('/alyuminy-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def alyuminy_material():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {'providers':[], "amount":[]}
        material_id = request.args.get("material_id")
        typ = request.args.get("type")
        color = request.args.get("color")
        thkn = request.args.get("thickness")
        if typ or color or thkn:
            data = filter_amount(name="aluminy_amount", type=typ, thickness=thkn, color1=color)
            return jsonify(data)
        elif material_id is not None:
            return jsonify(aluminy_schema.dump(Aluminy.query.get_or_404(material_id)))
        materials = Aluminy.query.order_by(Aluminy.date.desc()).all()
        amounts = AluminyAmount.query.all()
        data['providers'] = aluminy_schemas.dump(materials)
        data['amount'] = al_amount_schema.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        data = request.get_json()
        try:
            surface = add_aluminy_amount(thickness=data.get('thickness'), width=data.get('list_width', 1.22),
                color=data.get('color'), type=data.get('type_aluminy'), length=data.get('list_length'), roll_weight=data.get('roll_weight'), quantity=data.get('quantity'))
            material = Aluminy(**data, surface = surface)
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
                extra_sum = data.get("payed_price_s") - material.payed_price_s
                surface = update_aluminy_amount(material=material, thickness=data.get('thickness', None), color=data.get('color',None),
                    type=data.get('type_aluminy',None), list_length=data.get('list_length', material.list_length),
                    list_width=data.get('list_width', material.list_width), roll_weight=data.get('roll_weight', material.roll_weight), quantity=data.get('quantity', material.quantity))
                material.color = data.get('color', material.color)
                material.surface += surface
                material.thickness = data.get('thickness', material.thickness)
                material.list_width = data.get('list_width', material.list_width)
                material.list_length = data.get('list_length', material.list_length)
                material.quantity = data.get('quantity', material.quantity)
                material.roll_weight = data.get('roll_weight', material.roll_weight)
                material.price_per_kg = data.get('price_per_kg', material.price_per_kg)
                material.total_price_d = data.get('total_price_d', material.total_price_d)
                material.total_price_s = data.get('total_price_s', material.total_price_s)
                material.payed_price_d = data.get('payed_price_d', material.payed_price_d)
                material.payed_price_s = data.get('payed_price_s', material.payed_price_s)
                material.debt_d = data.get('debt_d', material.debt_d)
                material.debt_s = data.get('debt_s', material.debt_s)
                material.provider = data.get('provider', material.provider)
                material.date = data.get('date', material.date)
                material.surface = surface
                db.session.commit()
                balance_minus(extra_sum)
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get("material_id")
            material = db.get_or_404(Aluminy, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# kley xomashyo malumot kiritish
@bp.route('/glue-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def glue_material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {}
        material_id = request.args.get("material_id")
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            data['providers'] = glue_schemas.dump(Glue.query.filter(Glue.date.between(f"{from_d}", f"{to_d}")).order_by(Glue.date.desc()).all())
            data['amount'] = glue_amount_schemas.dump(GlueAmount.query.all())
            return jsonify(data)
        if material_id is not None:
            return jsonify(glue_schema.dump(Glue.query.get_or_404(material_id)))
        materials = Glue.query.all()
        amounts = GlueAmount.query.all()
        data['providers'] = glue_schemas.dump(materials)
        data['amount'] = glue_amount_schemas.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            surface = add_glue_amount(width=data.get("width", 1.22), length=data.get("length"), roll_weight=data.get("weight"), quantity=data.get("quantity"))
            material = Glue(**data, surface = surface)
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
                extra_sum = data.get("payed_price_s") - material.payed_price_s
                surface = update_glue_amount(material=material, length=data.get('length', material.length), width=data.get('width', material.width), roll_weight=data.get('weight', material.weight), quantity=data.get('quantity', material.quantity))
                material.thickness = data.get('thickness', material.thickness)
                material.width = data.get('width', material.width)
                material.length = data.get('length', material.length)
                material.quantity = data.get('quantity', material.quantity)
                material.surface += surface
                material.weight = data.get('weight', material.weight)
                material.price_per_kg = data.get('price_per_kg', material.price_per_kg)
                material.total_price_d = data.get('total_price_d', material.total_price_d)
                material.total_price_s = data.get('total_price_s', material.total_price_s)
                material.payed_price_d = data.get('payed_price_d', material.payed_price_d)
                material.payed_price_s = data.get('payed_price_s', material.payed_price_s)
                material.debt_d = data.get('debt_d', material.debt_d)
                material.debt_s = data.get('debt_s', material.debt_s)
                material.provider = data.get('provider', material.provider)
                db.session.commit()
                balance_minus(extra_sum)
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Glue, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# nakleyka xomashyo malumot kiritish
@bp.route('/sticker-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def sticker_material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {'providers':[], 'amount':[]}
        material_id = request.args.get("material_id")
        typ = request.args.get("type")
        if typ:
            data = filter_amount(name="sticker_amount", type=typ)
            return jsonify(data)
        if material_id is not None:
            return jsonify(sticker_schema.dump(Sticker.query.get_or_404(material_id)))
        data = {}
        materials = Sticker.query.all()
        amounts = StickerAmount.query.all()
        data['providers'] = sticker_schemas.dump(materials)
        data['amount'] = sticker_amount_schemas.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            surface = add_sticker_amount(width=data.get('width', 1.22),  type=data.get('type_sticker'), length=data.get('length'), quantity=data.get('quantity'))
            material = Sticker(**data, surface = surface)
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
                extra_sum = data.get("payed_price_s") - material.payed_price_s
                surface = update_sticker_amount(material=material,type=data.get('type_sticker', material.type_sticker), length=data.get('length', material.length), width=data.get('width', material.width),  quantity=data.get('quantity', material.quantity))
                material.type_sticker = data.get('type_sticker', material.type_sticker)
                material.width = data.get('width', material.width)
                material.length = data.get('length', material.length)
                material.quantity = data.get('quantity', material.quantity)
                material.surface += surface
                material.total_price_d = data.get('total_price_d', material.total_price_d)
                material.total_price_s = data.get('total_price_s', material.total_price_s)
                material.payed_price_d = data.get('payed_price_d', material.payed_price_d)
                material.payed_price_s = data.get('payed_price_s', material.payed_price_s)
                material.debt_d = data.get('debt_d', material.debt_d)
                material.debt_s = data.get('debt_s', material.debt_s)
                material.provider = data.get('provider', material.provider)
                db.session.commit()
                balance_minus(extra_sum)
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Sticker, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# alc_kg, alc_kg_s = 1.4, 5.922   # alyuminiy rangli kg
# al_kv = 3                       # alyuminiy kv
# g_gr, g_gr_s = 0.27, 1.2906     # kley gr
# g_kv = 3                        # kley kv
# s_kv, s_kv_s = 3, 0.69          # nakleyka
# grn_kg, grn_s = 10.3, 8.24      # granula
# al_kg, al_kg_s = 1.4, 5.24    # alyuminiy kg

# prixod
@bp.route('/make-alyukabond', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def make_aluykabond():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {'providers':[], 'amount':[]}
        material_id = request.args.get("material_id")
        typ = request.args.get("type")
        color1 = request.args.get("color1")
        color2 = request.args.get("color2")
        thkn = request.args.get("al_thickness")
        if typ or color1 or color2 or thkn:
            data = filter_amount(name="alyukabond_amount", type=typ, thickness=thkn, color1=color1, color2=color2)
            return jsonify(data)
        if material_id is not None:
            return jsonify(alyukabond_schema.dump(Alyukabond.query.get_or_404(material_id)))
        alyukabonds = Alyukabond.query.all()
        alyukabond_ammounts = AlyukabondAmount.query.all()
        data = {
            'alyukabond':alyukabond_schemas.dump(alyukabonds),
            'alyukabond_amount':alyukabond_amount_schema.dump(alyukabond_ammounts)
        }
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            turi = data.get('type_product')
            rangi1 = data.get('color1')
            rangi2 = data.get('color2', None)
            qalinligi = data.get('al_thickness')
            yuza = data.get('list_length') * data.get('list_width', 1.22)
            ogirlik = {
                    "alyuminy":1.4,
                    "glue":0.27,
                    "granula":10.3
                }
            sort = request.get_json().get('sort')
            miqdor = request.get_json().get('quantity')
            msg = check(turi=turi, rangi1=rangi1, rangi2=rangi2, qalinligi=qalinligi, yuza=yuza, ogirlik=ogirlik, sort=sort, miqdor=miqdor)
            if msg == 'success':
                alyukabond = Alyukabond(**data)
                db.session.add(alyukabond)
                add_alyukabond_amount(type=turi, color1=rangi1, color2=rangi2, length=data.get('list_length'), al_thickness=qalinligi, product_thickness=data.get('product_thickness'), quantity=miqdor)
                return jsonify(msg='Success')
            else:
                return jsonify(msg=msg)
        except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            data = request.get_json()
            material_id = request.args.get('material_id')
            try:
                material = db.get_or_404(Alyukabond, material_id)
                update_alyukabond_amount(material=material, type=data.get('type_product', material.type_product), sort=data.get('sort', material.sort), color1=data.get('color1', material.color1),
                    color2=data.get('color2', material.color2), length=data.get('list_length', material.list_length), width=data.get('list_width', material.list_width), al_thickness=data.get('al_thickness', material.al_thickness),
                    product_thickness=data.get('product_thickness', material.product_thickness), quantity=data.get('quantity', material.quantity))
                material.name = data.get('name', material.name)
                material.size = data.get('size', material.size)
                material.type_product = data.get('type_product', material.type_product)
                material.sort = data.get('sort', material.sort)
                material.color1 = data.get('color1', material.color1)
                material.color2 = data.get('color2', material.color2)
                material.list_length = data.get('list_length', material.list_length)
                material.list_width = data.get('list_width', material.list_width)
                material.al_thickness = data.get('al_thickness', material.al_thickness)
                material.product_thickness = data.get('product_thickness', material.product_thickness)
                material.quantity = data.get('quantity', material.quantity)
                material.provider = data.get('provider', material.provider)
                db.session.commit()
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get('material_id')
            material = db.get_or_404(Alyukabond, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# sklad
@bp.route('/warehouse')
@jwt_required()
def warehouse():
    data = {}
    alyukabond_amount = AlyukabondAmount.query.all()
    alyuminy_amount = AluminyAmount.query.all()
    glue_amount = GlueAmount.query.all()
    sticker_amount = StickerAmount.query.all()
    data["aluminy"] = al_amount_schema.dump(alyuminy_amount)
    data["glue"] = glue_amount_schemas.dump(glue_amount)
    data["sticker"] = sticker_amount_schemas.dump(sticker_amount)
    data["alyukabond"] = alyukabond_amount_schema.dump(alyukabond_amount)
    return jsonify(data)


# mahsulot sotish
@bp.route('/create-sale', methods=['GET', 'POST', 'PUT', 'PATCH'])
@jwt_required()
def create_sale():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        data = request.get_json()
        try:
            saled = SaledProduct(
                driver = data.get('driver'),
                customer = data.get('customer'),
                agreement_num = data.get('agreement_num'),
                total_price_d = data.get('total_price_d'),
                total_price_s = data.get('total_price_s'),
                payed_price_d = data.get('payed_price_d'),
                payed_price_s = data.get('payed_price_s'),
                debt_d = data.get('debt_d'),
                debt_s = data.get('debt_s')
                )
            db.session.add(saled)
            db.session.commit()
            for product in data.get('products'):   # [{'id':1, 'quantity':1},...]
                prd = db.get_or_404(AlyukabondAmount, product['id'])
                # total_price +=prd.price
                if prd.quantity < product['quantity']:
                    db.session.delete(saled)
                    db.session.commit()
                    return jsonify(msg="There isn't enough product in warehouse")
                prd.quantity -= product['quantity']
                selected = SelectedProduct(saled_id=saled.id, product_id=prd.id, quantity=product['quantity'])
                db.session.add(selected)
                db.session.commit()
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
        else:
            balance_add(data.get('payed_price_s'))
            return jsonify(msg="Created")
    elif request.method == 'GET':
        sales = SaledProduct.query.all()
        return jsonify(saled_product_schema.dump(sales))
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            id = request.args.get('saled_id')
            data = request.get_json()
            saled = db.get_or_404(SaledProduct, id)
            selected = db.session.execute(db.select(SelectedProduct).filter_by(saled_id=saled.id)).scalars().all()
            lst = selected.copy()
            for product in data.get('products'):
                for st in selected:
                    if product['id'] == st.product_id:
                        prd = db.get_or_404(AlyukabondAmount, product['id'])
                        extra_quantity = product['quantity'] - st.quantity
                        if prd.quantity < extra_quantity:
                            return jsonify(msg="There isn't enough alyukabond in warehouse")
                        prd.quantity -= extra_quantity
                        st.quantity = product['quantity']
                        lst.remove(st)
                    else:
                        prd = AlyukabondAmount.query.get(product['id'])
                        if prd and prd.quantity < product['quantity']:
                            return jsonify(msg="There isn't enough alyukabond in warehouse")
                        prd.quantity -= product['quantity']
                        selected = SelectedProduct(saled_id=saled.id, product_id=prd.id, quantity=product['quantity'])
                        db.session.add(selected)
            for s in lst:
                db.session.delete(s)
            extra_sum = data.get('payed_price_s', saled.payed_price_s) - saled.payed_price_s
            # if saled.payed_price_s < data.get('payed_price_s'):

            saled.driver = data.get('driver', saled.driver)
            saled.customer = data.get('customer', saled.customer)
            saled.vehicle_number = data.get('vehicle_number', saled.vehicle_number)
            saled.agreement_num = data.get('agreement_num', saled.agreement_num)
            saled.total_price_d = data.get('total_price_d', saled.total_price_d)
            saled.total_price_s = data.get('total_price_s', saled.total_price_s)
            saled.payed_price_d = data.get('payed_price_d', saled.payed_price_d)
            saled.payed_price_s = data.get('payed_price_s', saled.payed_price_s)
            saled.debt_d = data.get('debt_d', saled.debt_d)
            saled.debt_s = data.get('debt_s', saled.debt_s)
            db.session.commit()
            balance_add(extra_sum)
            return jsonify(msg='Success')
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(SaledProduct, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# sebestoymost
@bp.route('/price')
def alyukabond_price():
    color1 = request.args.get('color1')
    color2 = request.args.get('color2')
    thkn = int(request.args.get('al_thikness', 0))
    typ = int(request.args.get('type', 0))
    from_d = request.args.get('from')
    to_d = request.args.get('to')
    aluminy_color = Aluminy.query.filter(Aluminy.color==f"{color1}", Aluminy.type_aluminy==typ, Aluminy.thickness==thkn, Aluminy.date.between(f"{from_d}", f"{to_d}")).order_by(Aluminy.date.desc()).first()
    aluminy = Aluminy.query.filter(Aluminy.color==color2, Aluminy.type_aluminy==typ, Aluminy.thickness==thkn, Aluminy.date.between(f"{from_d}", f"{to_d}")).order_by(Aluminy.date.desc()).first()
    glue = Glue.query.filter(Glue.date.between(f"{from_d}", f"{to_d}")).order_by(Glue.date.desc()).first()
    sticker = Sticker.query.filter(Sticker.date.between(f"{from_d}", f"{to_d}"), Sticker.type_sticker==typ).order_by(Sticker.date.desc()).first()
    material = GranulaMaterial.query.filter(GranulaMaterial.date.between(f"{from_d}", f"{to_d}" )).first()
    aluminy_color_price = round((aluminy_color.total_price_d / aluminy_color.roll_weight * aluminy_color.quantity) * 1.4, 2) if aluminy_color is not None else 0
    aluminy_price = round((aluminy.total_price_d / aluminy.roll_weight * aluminy.quantity) * 1.4, 2) if aluminy is not None else 0
    glue_price = round((glue.total_price_d / glue.weight * glue.quantity) * 0.27, 2) if glue is not None else 0
    sticker_price = round((sticker.total_price_d / sticker.surface) * 3, 2) if sticker is not None else 0
    granula = round((material.total_price / material.weight) * 10.3, 2) if material is not None else 0
    data = {
        "aluminy_color1_price":aluminy_color_price,
        "aluminy_color2_price":aluminy_price,
        "glue_price":glue_price,
        "sticker_price":sticker_price,
        "granula":granula,
        "total":aluminy_color_price + aluminy_price + glue_price + sticker_price + granula,
    }
    return jsonify(data)


# xisobot sotib olingan
@bp.route('/report/purchase')
@jwt_required()
def report():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from').split('-')
        to_d = request.args.get('to').split('-')
        fr = request.args.get('filter', None)
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        if fr is None:
            aluminy = Aluminy.query.filter(Aluminy.date.between(d, s)).all()
            glue = Glue.query.filter(Glue.date.between(d, s)).all()
            sticker = Sticker.query.filter(Sticker.date.between(d, s)).all()
            alyukabond = Alyukabond.query.filter(Alyukabond.date.between(d, s)).all()
            saled = SaledProduct.query.filter(Alyukabond.date.between(d, s)).all()
            data = {
                "aluminy":aluminy_schemas.dump(aluminy),
                "glue":glue_schemas.dump(glue),
                "sticker":sticker_schemas.dump(sticker),
                "saled":saled_product_schema.dump(saled),
                "alyukabond":alyukabond_schema.dump(alyukabond)
            }
        else:
            objects = {
                "aluminy":aluminy_schemas.dump(Aluminy.query.filter(Aluminy.date.between(d, s)).all()),
                "glue":glue_schemas.dump(Glue.query.filter(Glue.date.between(d, s)).all()),
                "sticker":sticker_schemas.dump(Sticker.query.filter(Sticker.date.between(d, s)).all()),
                "saled":saled_product_schema.dump(SaledProduct.query.filter(Alyukabond.date.between(d, s)).all()),
                "alyukabond":alyukabond_schema.dump(Alyukabond.query.filter(Alyukabond.date.between(d, s)).all())
            }.get(fr, None)
            data = {f"{fr}":objects}
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


# Mahsulot xisobot
@bp.route('/report/product')
@jwt_required()
def report_product():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from').split('-')
        to_d = request.args.get('to').split('-')
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        alyukabond = Alyukabond.query.filter(Alyukabond.date.between(d, s)).all()
        data = {
            "alyukabond":alyukabond_schema.dump(alyukabond)
        }
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


# Sotilgan tovar xisobot
@bp.route('/report/saled')
@jwt_required()
def report_saled():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from').split('-')
        to_d = request.args.get('to').split('-')
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        saled = SaledProduct.query.filter(Alyukabond.date.between(d, s)).all()
        data = {
            "saled":saled_product_schema.dump(saled)
        }
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


# Qarzlar xisobot
@bp.route('/report/debt')
@jwt_required()
def report_debt():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from').split('-')
        to_d = request.args.get('to').split('-')
        fr = request.args.get('filter', None)
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        total_aluminy = Aluminy.query.with_entities(func.sum(Aluminy.debt_d), func.sum(Aluminy.debt_s)).filter(Aluminy.date.between(d, s)).all()
        total_glue = Glue.query.with_entities(func.sum(Glue.debt_d), func.sum(Glue.debt_s)).filter(Glue.date.between(d, s)).all()
        total_sticker = Sticker.query.with_entities(func.sum(Sticker.debt_d), func.sum(Sticker.debt_s)).filter(Sticker.date.between(d, s)).all()
        data = {
            "total_d_aluminy":total_aluminy[0][0],
            "total_s_aluminy":total_aluminy[0][1],
            "total_d_glue":total_glue[0][0],
            "total_s_glue":total_glue[0][1],
            "total_d_sticker":total_sticker[0][0],
            "total_s_sticker":total_sticker[0][1]
        }
        if fr is not None:
            objects = {
                "aluminy":aluminy_schemas.dump(Aluminy.query.filter(Aluminy.date.between(d, s), Aluminy.debt_d>0).all()),
                "glue":glue_schemas.dump(Glue.query.filter(Glue.date.between(d, s), Glue.debt_d>0).all()),
                "sticker":sticker_schemas.dump(Sticker.query.filter(Sticker.date.between(d, s), Sticker.debt_d>0).all()),
                "saled":saled_product_schema.dump(SaledProduct.query.filter(SaledProduct.date.between(d, s), SaledProduct.debt_d>0).all()),
                "alyukabond":alyukabond_schema.dump(Alyukabond.query.filter(Alyukabond.date.between(d, s)).all())
            }.get(fr, None)
            data[fr] =  objects
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


@bp.route('/pay-debt/<string:name>', methods=['POST'])
def pay_debt(name):
    data = request.get_json()
    material = {
        'aluminy':Aluminy.query.get(data.get('id')),
        'glue':Glue.query.get(data.get('id')),
        'sticker':Sticker.query.get(data.get('id')),
        'alyukabond':SaledProduct.query.get(data.get('id'))
    }.get(name, None)
    if material.debt_s >= data.get('amount'):
        material.total_price_s = material.total_price_s
        material.payed_price_s += data.get('amount')
        material.debt_s -= data.get('amount')
        payed = {
            'aluminy':PayedDebt(amount=data.get('amount'), aluminy_id = material.id),
            'glue':PayedDebt(amount=data.get('amount'), glue_id = material.id),
            'sticker':PayedDebt(amount=data.get('amount'), sticker_id = material.id),
            'alyukabond':PayedDebt(amount=data.get('amount'), saled_id = material.id)
        }.get(name, None)
        db.session.add(payed)
        db.session.commit()
        balance_add(data.get('amount')) if name=='alyukabond' else balance_minus(data.get('amount'))
        return jsonify(msg="Success")
    return jsonify(msg="You are entered more then debt")


# Haqlar xisobot
@bp.route('/report/fee')
@jwt_required()
def report_fee():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from').split('-')
        to_d = request.args.get('to').split('-')
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        total_alyukabond = SaledProduct.query.with_entities(func.sum(SaledProduct.debt_d), func.sum(SaledProduct.debt_s)).filter(SaledProduct.date.between(d, s)).all()
        aluminy = [{'debt_d':a.debt_d, 'debt_s':a.debt_s, 'date':f"{a.date:%Y-%m-%d}", 'customer':a.customer} for a in SaledProduct.query.filter(SaledProduct.date.between(d, s)).all()]
        data = {
            "product":aluminy,
            "total_d_product":total_alyukabond[0][0],
            "total_s_product":total_alyukabond[0][1]
            }
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


# balans
@bp.route('/balance')
def balance():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from', f"{date.today():%Y-%m-%d}").split('-')
        to_d = request.args.get('to', f"{date.today():%Y-%m-%d}").split('-')
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        balance = Balance.query.filter_by(index1=True).first()
        saled = SaledProduct.query.with_entities(func.sum(SaledProduct.payed_price_d)).filter(SaledProduct.date.between(d, s)).all()
        aluminy = Aluminy.query.with_entities(func.sum(Aluminy.total_price_d)).filter(Aluminy.date.between(d, s)).all()
        glue = Glue.query.with_entities(func.sum(Glue.total_price_d)).filter(Glue.date.between(d, s)).all()
        sticker = Sticker.query.with_entities(func.sum(Sticker.total_price_d)).filter(Sticker.date.between(d, s)).all()
        exp = Expence.query.with_entities(func.sum(Expence.price)).all()
        print(saled, aluminy, glue, sticker)
        data = {
            "balance":balance.amount if balance else 0,
            "profit":(saled[0][0] - (aluminy[0][0] + glue[0][0] + sticker[0][0])) if saled[0][0] and aluminy[0][0] and glue[0][0] and sticker[0][0] else None,
            "expence":exp[0][0],
            "total":saled[0][0]
        }
        return jsonify(data)
    else:
        return jsonify(msg="You have not authority to this action"), 401


@bp.route('/transaction', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def transaction():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        if request.method == 'GET':
            id = request.args.get("transaction_id", None)
            status = request.args.get("status")
            if id is not None:
                tr = db.get_or_404(WriteTransaction, id)
                return jsonify(transaction_schema.dump(tr))
            trs = WriteTransaction.query.filter_by(status=status).all()
            return jsonify(transaction_schemas.dump(trs))
        elif request.method == 'POST':
            data = request.get_json()
            if data['status'] == 'add':
                write = WriteTransaction(
                        amount=data.get('amount'),
                        user = user.username,
                        description = data.get('description'),
                        status = data.get('status')
                        )
                db.session.add(write)
                db.session.commit()
                balance_add(data.get("amount"))
            else:
                write = WriteTransaction(
                        amount=data.get('amount'),
                        user = user.username,
                        description = data.get('description'),
                        status = data.get('status')
                        )
                db.session.add(write)
                db.session.commit()
                balance_minus(data.get("amount"))
            return jsonify(msg='Success')
        else:
            id = request.args.get("transaction_id", None)
            tr = db.get_or_404(WriteTransaction, id)
            db.session.delete(tr)
            db.session.commit()
            return jsonify(msg="Deleted")
    else:
        return jsonify(msg="You are not admin"), 401


@bp.route('/report-excel/<int:id>')
def report_excel(id):
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        source_excel_file = 'main/alyukabond/report_template.xlsx'
        destination_excel_file = 'report/report.xlsx'
        shutil.copy2(source_excel_file, destination_excel_file)
        sheet_name = 'Накладная'
        destination_wb = load_workbook(destination_excel_file)
        destination_sheet = destination_wb[sheet_name]
        count = 15
        saled = SaledProduct.query.get(id)
        destination_sheet["C3"] = saled.date
        destination_sheet["D5"] = saled.agreement_num
        destination_sheet["E9"] = saled.customer
        destination_sheet["E12"] = saled.driver
        destination_sheet["M12"] = saled.vehicle_number
        for product in saled.products:
            typ = {
                "100":"gl",
                "150":"mt",
                "450":"pdr"
            }.get(product.product.type_product, None)
            count +=1
            data_to_write = {
                f'C{count}': product.product.name if product.product.name else "Alyukabond",
                f'L{count}': f"{product.product.color1}, {product.product.color2}, {typ}",
                f'M{count}': "list",
                f'N{count}': product.product.quantity
            }
            for cell_address, value in data_to_write.items():
                destination_sheet[cell_address] = value
            destination_wb.save(destination_excel_file)
        destination_wb.close()
        return send_from_directory("../report", "report.xlsx")
    else:
        return jsonify(msg="You have not authority to this action"), 401


@bp.route('/makaron', methods=['GET','POST', 'DELETE'])
def add_makaron():
    if request.method == 'GET':
        makaron = Makaron.query.all()
        return jsonify(makaron_schema.dump(makaron))
    elif request.method == 'POST':
        data = request.get_json()
        makaron = Makaron.query.filter_by(type_al = data.get('type'),color1 = data.get('color1'),color2 = data.get('color2'),
            al_thickness = data.get('thickness'),list_length = data.get('length')).first()
        if makaron is None:
            makaron = Makaron(
                type_al = data.get('type'),
                color1 = data.get('color1'),
                color2 = data.get('color2'),
                al_thickness = data.get('thickness'),
                list_length = data.get('length'),
                weight = 0
            )
            db.session.add(makaron)
        makaron.weight += data.get('weight')
        db.session.commit()
        return jsonify(msg="Created")
    else:
        id = request.args.get('makaron_id')
        weight = int(request.args.get("weight"))
        amount = int(request.args.get('amount'))
        balance_add(amount)
        makaron = db.get_or_404(Makaron, id)
        makaron.weight -= weight
        db.session.commit()
        return jsonify(msg="Success")

