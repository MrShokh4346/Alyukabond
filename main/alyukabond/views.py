from flask import jsonify, request, redirect, url_for
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from main.serializers import *
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import  send_from_directory, url_for, jsonify, request
from uuid import uuid1
from sqlalchemy.exc import SQLAlchemyError
import os
from openpyxl import Workbook, load_workbook
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from .amounts import * 



@bp.route('/exchange-rate', methods=['GET', 'POST'])
def exchange_rate():
    if request.method == 'POST':
        rate = ExchangeRate(rate=request.get_json().get('rate'))
        db.session.add(rate)
        db.session.commit()
        return jsonify(msg='Success')
    else:
        rate = ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
        data = {"rate":rate.rate if rate else None, "date":rate.date if rate else None}
        return jsonify(data)


# aluminiy xomashyo malumot kiritish
@bp.route('/alyuminy-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def alyuminy_material():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {}
        materials = Aluminy.query.all()
        amounts = AluminyAmount.query.all()
        data['providers'] = aluminy_schemas.dump(materials)
        data['amount'] = al_amount_schema.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        if user.role == 'a':
            data = request.get_json()
            amount_id = request.args.get('amount_id', None)
            try:
                surface = add_aluminy_amount(id=amount_id, thickness=data.get('thickness'), width=data.get('list_width'), 
                    color=data.get('color'), type=data.get('type_aluminy'), length=data.get('list_length'), roll_weight=data.get('roll_weight'), quantity=data.get('quantity'))
                material = Aluminy(**data, surface = surface)
                db.session.add(material)
                db.session.commit()
                return jsonify(msg="Success"), 201
            except AssertionError as err:
                return jsonify(msg="This size already exists")
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        id = request.args.get('material_id')
        amount_id = request.args.get('amount_id', 0)
        if user.role == 'a':
            data = request.get_json()
            material = Aluminy.query.get(id)
            surface = update_aluminy_amount(material=material, thickness=data.get('thickness', None), color=data.get('color',None),
                type=data.get('type_aluminy',None), list_length=data.get('list_length', material.list_length), 
                list_width=data.get('list_width', material.list_width), roll_weight=data.get('roll_weight', material.roll_weight), quantity=data.get('quantity', material.quantity))
            material.color = data.get('color', material.color)
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
            return jsonify(msg='Success')
        return jsonify("You are not admin"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Aluminy, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You are not admin"), 401


# kley xomashyo malumot kiritish
@bp.route('/glue-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def glue_material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {}
        materials = Glue.query.all()
        amounts = GlueAmount.query.all()
        data['providers'] = glue_schemas.dump(materials)
        data['amount'] = glue_amount_schemas.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        if user.role == 'a':
            data = request.get_json()
            surface = add_glue_amount(width=data.get("width", 2.44), length=data.get("length"), roll_weight=data.get("weight"), quantity=data.get("quantity"))
            material = Glue(**data, surface = surface)
            db.session.add(material)
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            data = request.get_json()
            material = Glue.query.get(id)
            surface = update_glue_amount(material=material,length=data.get('length', material.length), width=data.get('width', material.width), roll_weight=data.get('weight', material.weight), quantity=data.get('quantity', material.quantity))
            material.thickness = data.get('thickness', material.thickness)
            material.width = data.get('width', material.width)
            material.length = data.get('length', material.length)
            material.quantity = data.get('quantity', material.quantity)
            material.surface =  surface
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
            return jsonify(msg='Success')
        return jsonify("You are not admin"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Glue, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You are not admin"), 401


# nakleyka xomashyo malumot kiritish
@bp.route('/sticker-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def sticker_material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        data = {}
        materials = Sticker.query.all()
        amounts = StickerAmount.query.all()
        data['providers'] = sticker_schemas.dump(materials)
        data['amount'] = sticker_amount_schemas.dump(amounts)
        return jsonify(data)
    elif request.method == 'POST':
        if user.role == 'a':
            data = request.get_json()
            amount_id = request.args.get('amount_id', 0)
            surface = add_sticker_amount(id=amount_id, width=data.get('width'),  type=data.get('type_sticker'), length=data.get('length'), quantity=data.get('quantity'))
            material = Sticker(**data, surface = surface)
            db.session.add(material)
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            data = request.get_json()
            material = Sticker.query.get(id)
            surface = update_sticker_amount(material=material,type=data.get('type_sticker', material.type_sticker), length=data.get('length', material.length), width=data.get('width', material.width),  quantity=data.get('quantity', material.quantity))
            material.type_sticker = data.get('type_sticker', material.type_sticker)
            material.width = data.get('width', material.width)
            material.length = data.get('length', material.length)
            material.quantity = data.get('quantity', material.quantity)
            material.weight = data.get('weight', material.weight)
            material.surface = surface
            material.price_per_surface = data.get('price_per_surface', material.price_per_surface)
            material.total_price_d = data.get('total_price_d', material.total_price_d)
            material.total_price_s = data.get('total_price_s', material.total_price_s)
            material.payed_price_d = data.get('payed_price_d', material.payed_price_d)
            material.payed_price_s = data.get('payed_price_s', material.payed_price_s)
            material.debt_d = data.get('debt_d', material.debt_d)
            material.debt_s = data.get('debt_s', material.debt_s)
            material.provider = data.get('provider', material.provider)
            db.session.commit()
            return jsonify(msg='Success')
        return jsonify("You are not admin"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(Sticker, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You are not admin"), 401


def check(turi=None, rangi=None, qalinligi=None, yuza=None, ogirlik=None, sort=1, miqdor=1):
    for obj in ['alyuminy', 'sticker', 'glue', 'granula']:
        amount = {
            'alyuminy': AluminyAmount.query.filter_by(color=rangi, type_aluminy=turi, thickness=qalinligi).first(),
            'sticker': StickerAmount.query.filter_by(type_sticker=turi).first(),
            'glue': GlueAmount.query.filter_by(index1=True).first(),
            'granula':GranulaAmount.query.filter_by(sklad=False).first()
        }.get(obj, False)
        
        if amount is not None and (amount.surface > yuza * sort if obj=="alyuminy" else yuza):
            if amount.surface if obj!="granula" else False:
                amount.surface -= yuza * sort * miqdor if obj=="alyuminy" else yuza * miqdor
            if amount.weight if obj!="sticker" else False:
                amount.weight -= ogirlik[obj] * miqdor
            msg="success"
            db.session.commit()
        else:
            msg=f"There isn't enaugh {obj} in warehouse"
            break
    return msg


# alc_kg, alc_kg_s = 1.4, 5.922   # alyuminiy rangli kg
# al_kv = 3                       # alyuminiy kv 
# g_gr, g_gr_s = 0.27, 1.2906     # kley gr
# g_kv = 3                        # kley kv
# s_kv, s_kv_s = 3, 0.69          # nakleyka
# grn_kg, grn_s = 10.3, 8.24      # granula
# al_kg, al_kg_s = 1.4, 5.24    # alyuminiy kg

# prixod
@bp.route('/make-alyukabond', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
def make_aluykabond():
    data = request.get_json()
    turi = request.get_json().get('type')
    rangi = request.get_json().get('color')
    qalinligi = request.get_json().get('aluminy_thickness')
    yuza = request.get_json().get('length') * request.get_json().get('width', 1.22)
    ogirlik = {
            "alyuminy":1.4,
            "glue":0.27,
            "granula":10.3
        }
    sort = request.get_json().get('sort')
    miqdor = request.get_json().get('quantity')
    msg = check(turi, rangi, qalinligi, yuza, ogirlik, sort, miqdor)
    if msg == 'success':
        alyukabond = Alyukabond(
            name = data.get('name'),
            size = data.get('size'),
            type_product = data.get('type'),
            sort = data.get('sort'),
            color = data.get('color'),
            list_length = data.get('length'),
            list_width = data.get('width'),
            al_thickness = data.get('aluminy_thickness'),
            product_thickness = data.get('product_thickness'),
            quantity = data.get('quantity'),
            provider = data.get('provider')
        )
        db.session.add(alyukabond)
        amount_id = request.args.get('amount_id', 0)
        amount = AlyukabondAmount.query.get(amount_id)
        if amount:
            pass
        else:
            obj = AlyukabondAmount.query.filter_by(
                                                type_product = data.get('type'),
                                                sort = data.get('sort'),
                                                color = data.get('color'),
                                                list_length = data.get('length'),
                                                al_thickness = data.get('aluminy_thickness'),
                                                product_thickness = data.get('product_thickness')).first()
            if obj:
                return jsonify(msg='This size already exists')
            else:
                amount = AlyukabondAmount(size = data.get('size'),
                                        type_product = data.get('type'),
                                        sort = data.get('sort'),
                                        color = data.get('color'),
                                        list_length = data.get('length'),
                                        list_width = data.get('width'),
                                        al_thickness = data.get('aluminy_thickness'),
                                        product_thickness = data.get('product_thickness'),
                                        quantity=0)
                db.session.add(amount)
                db.session.commit()
        amount.quantity += data.get('quantity')
        db.session.commit()
        return jsonify(msg='Success')
    else:
        return jsonify(msg=msg)


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
@bp.route('/create-sale', methods=['GET', 'POST'])
def create_sale():
    if request.method == 'POST':
        data = request.get_json()
        try:
            saled = SaledProduct(
                provider = data.get('provider'),
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
                selected = SelectedProduct(saled_id=saled.id, product_id=prd.id, quantity=product['quantity'])
                db.session.add(selected)
                db.session.commit()
        except:
            return jsonify(msg="Something went wrong")
        else:
            balance = Balance.query.filter_by(index1=True).first()
            if not balance:
                balance = Balance(amount=0)
                db.session.add(balance) 
                db.session.commit()
            balance.amount += data.get('total_price_d')
            db.session.commit()
            return jsonify(msg="Created")
    elif request.method == 'GET':
        sales = SaledProduct.query.all()
        return jsonify(saled_product_schema.dump(sales))


# alyukabond narx
@bp.route('/price')
def alyukabond_price():
    color = request.args.get('color')
    print(color)
    sort = request.args.get('sort')
    typ = int(request.args.get('type'))
    aluminy_color = Aluminy.query.filter_by(color=f"{color}", type_aluminy=typ).order_by(Aluminy.date.desc()).first_or_404() 
    aluminy = Aluminy.query.filter_by(color=None).order_by(Aluminy.date.desc()).first_or_404()
    glue = Glue.query.order_by(Glue.date.desc()).first_or_404()
    sticker = Sticker.query.order_by(Sticker.date.desc()).first_or_404()
    aluminy_color_price = (aluminy_color.roll_weight * aluminy_color.quantity / aluminy_color.total_price_d) * 1.4
    aluminy_price = (aluminy.roll_weight * aluminy.quantity / aluminy.total_price_d) * 1.4
    glue_price = (glue.weight * glue.quantity / glue.total_price_d) * 0.27
    sticker_price = (sticker.surface / sticker.total_price_d) * 3
    granula = 8.24 ##################################################################
    if sort == 2:
        data = {
            "aluminy_color_price":round(aluminy_color_price, 2),
            "glue_price":round(glue_price, 2),
            "sticker_price":round(sticker_price, 2),
            "granula":round(granula, 2),
            "total":round((aluminy_color_price * 2) + glue_price + sticker_price + granula, 2)
        }
    else:

        data = {
            "aluminy_color_price":round(aluminy_color_price, 2),
            "aluminy_price":round(aluminy_price, 2),
            "glue_price":round(glue_price, 2),
            "sticker_price":round(sticker_price, 2),
            "granula":round(granula, 2),
            "total":round(aluminy_color_price + aluminy_price + glue_price + sticker_price + granula, 2)
        }
    return jsonify(data)


# xisobot
@bp.route('/report')
@jwt_required()
def report():
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


# Mahsulot xisobot
@bp.route('/report/product')
@jwt_required()
def report_product():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    alyukabond = Alyukabond.query.filter(Alyukabond.date.between(d, s)).all()
    data = {
        "alyukabond":alyukabond_schema.dump(alyukabond)
    }
    return jsonify(data)


# Sotilgan tovar xisobot
@bp.route('/report/saled')
@jwt_required()
def report_saled():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    saled = SaledProduct.query.filter(Alyukabond.date.between(d, s)).all()
    data = {
        "saled":saled_product_schema.dump(saled)
    }
    return jsonify(data)


# Qarzlar xisobot
@bp.route('/report/debt')
@jwt_required()
def report_debt():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    total_aluminy = Aluminy.query.with_entities(func.sum(Aluminy.debt_d), func.sum(Aluminy.debt_s)).filter(Aluminy.date.between(d, s)).all()
    aluminy = [{'debt_d':a.debt_d, 'debt_s':a.debt_s, 'date':a.date, 'provider':a.provider, "id":a.id} for a in Aluminy.query.filter(Aluminy.date.between(d, s)).all()]
    total_glue = Glue.query.with_entities(func.sum(Glue.debt_d), func.sum(Glue.debt_s)).filter(Glue.date.between(d, s)).all()
    glue = [{'debt_d':a.debt_d, 'debt_s':a.debt_s, 'date':a.date, 'provider':a.provider, "id":a.id} for a in Glue.query.filter(Glue.date.between(d, s)).all()]
    sticker = [{'debt_d':a.debt_d, 'debt_s':a.debt_s, 'provider':a.provider, "id":a.id} for a in Sticker.query.filter(Sticker.date.between(d, s)).all()]
    total_sticker = Sticker.query.with_entities(func.sum(Sticker.debt_d), func.sum(Sticker.debt_s)).filter(Sticker.date.between(d, s)).all()
    data = {
        "aluminy":aluminy,
        "total_d_aluminy":total_aluminy[0][0],
        "total_s_aluminy":total_aluminy[0][1],

        "glue":glue,
        "total_d_glue":total_glue[0][0],
        "total_s_glue":total_glue[0][1],

        "sticker":sticker,
        "total_d_sticker":total_sticker[0][0],
        "total_s_sticker":total_sticker[0][1]

    }
    return jsonify(data)


# Haqlar xisobot
@bp.route('/report/fee')
@jwt_required()
def report_fee():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    total_alyukabond = SaledProduct.query.with_entities(func.sum(SaledProduct.debt_d), func.sum(SaledProduct.debt_s)).filter(SaledProduct.date.between(d, s)).all()
    aluminy = [{'debt_d':a.debt_d, 'debt_s':a.debt_s, 'date':a.date, 'provider':a.provider} for a in SaledProduct.query.filter(SaledProduct.date.between(d, s)).all()]
    data = {
        "product":aluminy,
        "total_d_product":total_alyukabond[0][0],
        "total_s_product":total_alyukabond[0][1]
        }
    return jsonify(data)


# balans
@bp.route('/balance')
def balance():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    balance = Balance.query.filter_by(index1=True).first()
    saled = SaledProduct.query.with_entities(func.sum(SaledProduct.payed_price_d)).filter(SaledProduct.date.between(d, s)).all()
    aluminy = Aluminy.query.with_entities(func.sum(Aluminy.total_price_d)).filter(Aluminy.date.between(d, s)).all()
    glue = Glue.query.with_entities(func.sum(Glue.total_price_d)).filter(Glue.date.between(d, s)).all()
    sticker = Sticker.query.with_entities(func.sum(Sticker.total_price_d)).filter(Sticker.date.between(d, s)).all()
    exp = Expence.query.with_entities(func.sum(Expence.price)).all()
    print((aluminy[0][0] + glue[0][0] + sticker[0][0]))
    data = {
        "balance":balance.amount if balance else 0,
        "profit":saled[0][0] - (aluminy[0][0] + glue[0][0] + sticker[0][0]),
        "expence":exp[0][0],
        "total":saled[0][0]
    }
    return jsonify(data)


@bp.route('/transaction', methods=['GET', 'POST', 'PUT', 'PATCH'])
def transaction():
    if request.method == 'GET':
        id = request.args.get("transaction_id", None)
        if id is not None:
            tr = db.get_or_404(WriteTransaction, id)
            return jsonify(transaction_schema.dump(tr))
        trs = WriteTransaction.query.all()
        return jsonify(transaction_schemas.dump(trs))
    elif request.method == 'POST':
        pass


@bp.route('/report-excel/<int:id>')
def report_excel(id):
    source_excel_file = 'main/alyukabond/report.xlsx'
    destination_excel_file = 'report/report1.xlsx'
    pdf_file = 'report/report1.pdf'
    shutil.copy2(source_excel_file, destination_excel_file)


    # Specify the sheet name
    sheet_name = 'Накладная'

    # Load the source workbook
    destination_wb = load_workbook(destination_excel_file)
    destination_sheet = destination_wb[sheet_name]
  
    count = 15
    saled = SaledProduct.query.get(id)
   

    destination_sheet["C3"] = saled.date
    destination_sheet["D5"] = saled.agreement_num
    destination_sheet["E9"] = saled.customer.split(' ', 1)[0]
    destination_sheet["M9"] = saled.customer.split(' ', 1)[1]
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
            f'L{count}': f"{product.product.color}, {typ}",
            f'M{count}': f"{product.product.list_width}, {product.product.list_length}, {product.product.product_thickness}",
            f'N{count}': product.product.quantity
        }
        for cell_address, value in data_to_write.items():
            destination_sheet[cell_address] = value
        destination_wb.save(destination_excel_file)
    destination_wb.close()
    return jsonify(data_to_write)