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
import os


# aluminiy xomashyo malumot kiritish
@bp.route('/alyuminy-material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def alyuminy_material():
    id = request.args.get('material_id')
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
            amount_id = request.args.get('amount_id', 0)
            amount = AluminyAmount.query.get(amount_id)
            if amount:
                pass
            else:
                obj = AluminyAmount.query.filter_by(thickness=request.get_json().get('thickness'), 
                                                width=request.get_json().get('list_width'),
                                                color=request.get_json().get('color')
                                                ).first()
                if obj:
                    return jsonify(msg='This size already exists')
                else:
                    amount = AluminyAmount(color = request.get_json().get('color'),
                                            thickness = request.get_json().get('thickness'),
                                            width = request.get_json().get('list_width'),
                                            length = 0,
                                            weight = 0
                                            )
                    db.session.add(amount)
                    db.session.commit()
            amount.length += request.get_json().get('list_length')
            amount.weight += request.get_json().get('roll_weight')
            db.session.commit()
            material = Aluminy(
                color = request.get_json().get('color'),
                thickness = request.get_json().get('thickness'),
                list_width = request.get_json().get('list_width'),
                list_length = request.get_json().get('list_length'),
                roll_weight = request.get_json().get('roll_weight'),
                price_per_kg = request.get_json().get('price_per_kg'),
                total_price_d = request.get_json().get('total_price_d'),
                total_price_s = request.get_json().get('total_price_s'),
                payed_price_d = request.get_json().get('payed_price_d'),
                payed_price_s = request.get_json().get('payed_price_s'),
                debt_d = request.get_json().get('debt_d'),
                debt_s = request.get_json().get('debt_s'),
                provider = request.get_json().get('provider'),
                date = request.get_json().get('date')
            )
            db.session.add(material)
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            material = Aluminy.query.get(id)
            material.color = request.get_json().get('color', material.color)
            material.thickness = request.get_json().get('thickness', material.thickness)
            material.list_width = request.get_json().get('list_width', material.list_width)
            material.list_length = request.get_json().get('list_length', material.list_length)
            material.roll_weight = request.get_json().get('roll_weight', material.roll_weight)
            material.price_per_kg = request.get_json().get('price_per_kg', material.price_per_kg)
            material.total_price_d = request.get_json().get('total_price_d', material.total_price_d)
            material.total_price_s = request.get_json().get('total_price_s', material.total_price_s)
            material.payed_price_d = request.get_json().get('payed_price_d', material.payed_price_d)
            material.payed_price_s = request.get_json().get('payed_price_s', material.payed_price_s)
            material.debt_d = request.get_json().get('debt_d', material.debt_d)
            material.debt_s = request.get_json().get('debt_s', material.debt_s)
            material.provider = request.get_json().get('provider', material.provider)
            material.date = request.get_json().get('date', material.date)
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
            amount_id = request.args.get('amount_id', 0)
            amount = GlueAmount.query.get(amount_id)
            if amount:
                pass
            else:
                obj = GlueAmount.query.filter_by(thickness=request.get_json().get('thickness'), 
                                                type_glue=request.get_json().get('type_glue')).first()
                if obj:
                    return jsonify(msg='This size already exists')
                else:
                    amount = GlueAmount(
                                        thickness = request.get_json().get('thickness'),
                                        type_glue = request.get_json().get('type_glue'),
                                        surface = 0,
                                        weight = 0
                                        )
                    db.session.add(amount)
                    db.session.commit()
            amount.surface += request.get_json().get('surface')
            amount.weight += request.get_json().get('weight')
            db.session.commit()
            material = Glue(
                type_glue = request.get_json().get('type_glue'),
                thickness = request.get_json().get('thickness'),
                surface = request.get_json().get('surface'),
                weight = request.get_json().get('weight'),
                price_per_kg = request.get_json().get('price_per_kg'),
                total_price_d = request.get_json().get('total_price_d'),
                total_price_s = request.get_json().get('total_price_s'),
                payed_price_d = request.get_json().get('payed_price_d'),
                payed_price_s = request.get_json().get('payed_price_s'),
                debt_d = request.get_json().get('debt_d'),
                debt_s = request.get_json().get('debt_s'),
                provider = request.get_json().get('provider')
            )
            db.session.add(material)
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            material = Glue.query.get(id)
            material.type_glue = request.get_json().get('type_glue', material.type_glue)
            material.thickness = request.get_json().get('thickness', material.thickness)
            material.surface = request.get_json().get('surface', material.surface)
            material.weight = request.get_json().get('weight', material.weight)
            material.price_per_kg = request.get_json().get('price_per_kg', material.price_per_kg)
            material.total_price_d = request.get_json().get('total_price_d', material.total_price_d)
            material.total_price_s = request.get_json().get('total_price_s', material.total_price_s)
            material.payed_price_d = request.get_json().get('payed_price_d', material.payed_price_d)
            material.payed_price_s = request.get_json().get('payed_price_s', material.payed_price_s)
            material.debt_d = request.get_json().get('debt_d', material.debt_d)
            material.debt_s = request.get_json().get('debt_s', material.debt_s)
            material.provider = request.get_json().get('provider', material.provider)
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
            amount_id = request.args.get('amount_id', 0)
            amount = StickerAmount.query.get(amount_id)
            if amount:
                pass
            else:
                obj = StickerAmount.query.filter_by(width=request.get_json().get('width'), 
                                                type_sticker=request.get_json().get('type_sticker')).first()
                if obj:
                    return jsonify(msg='This size already exists')
                else:
                    amount = StickerAmount(
                                        width = request.get_json().get('width'),
                                        type_sticker = request.get_json().get('type_sticker'),
                                        surface = 0,
                                        weight = 0
                                        )
                    db.session.add(amount)
                    db.session.commit()
            amount.surface += request.get_json().get('surface')
            amount.weight += request.get_json().get('weight')
            db.session.commit()
            material = Sticker(
                type_sticker = request.get_json().get('type_sticker'),
                width = request.get_json().get('width'),
                weight = request.get_json().get('weight'),
                surface = request.get_json().get('surface'),
                price_per_surface = request.get_json().get('price_per_surface'),
                total_price_d = request.get_json().get('total_price_d'),
                total_price_s = request.get_json().get('total_price_s'),
                payed_price_d = request.get_json().get('payed_price_d'),
                payed_price_s = request.get_json().get('payed_price_s'),
                debt_d = request.get_json().get('debt_d'),
                debt_s = request.get_json().get('debt_s'),
                provider = request.get_json().get('provider')
            )
            db.session.add(material)
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            material = Sticker.query.get(id)
            material.type_sticker = request.get_json().get('type_sticker', material.type_sticker)
            material.width = request.get_json().get('width', material.width)
            material.weight = request.get_json().get('weight', material.weight)
            material.surface = request.get_json().get('surface', material.surface)
            material.price_per_surface = request.get_json().get('price_per_surface', material.price_per_surface)
            material.total_price_d = request.get_json().get('total_price_d', material.total_price_d)
            material.total_price_s = request.get_json().get('total_price_s', material.total_price_s)
            material.payed_price_d = request.get_json().get('payed_price_d', material.payed_price_d)
            material.payed_price_s = request.get_json().get('payed_price_s', material.payed_price_s)
            material.debt_d = request.get_json().get('debt_d', material.debt_d)
            material.debt_s = request.get_json().get('debt_s', material.debt_s)
            material.provider = request.get_json().get('provider', material.provider)
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


# prixod
@bp.route('/make-alyukabond', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
def make_aluykabond():
    data = request.get_json()
    alc_kg, alc_kg_s = 1.4, 5.922   # alyuminiy rangli kg
    al_kv = 3                       # alyuminiy kv 
    g_gr, g_gr_s = 0.27, 1.2906     # kley gr
    g_kv = 3                        # kley kv
    s_kv, s_kv_s = 3, 0.69          # nakleyka
    grn_kg, grn_s = 10.3, 8.24      # granula
    alc_kg, alc_kg_s = 1.4, 5.24    # alyuminiy kg
    
    try:
        al_amount = AluminyAmount.query.filter_by(color=data.get('color'), 
                thickness=data.get('aluminy_thickness'), width=data.get('list_width')).first()
        if al_amount.length < (al_kv/data.get('list_width')) * data.get('quantity') and al_amount.weight < alc_kg * data.get('quantity'):
            return jsonify(msg="There isn't enough aluminy in warehouse")
        al_amount.length -= (al_kv/data.get('list_width')) * data.get('quantity')
        al_amount.weight -= alc_kg * data.get('quantity')

        g_amount = GlueAmount.query.filter_by(index1=True).first()
        if g_amount.surface < g_kv * data.get('quantity') and g_amount.weight < g_gr * data.get('quantity'):
            return jsonify(msg="There isn't enough glue in warehouse")
        g_amount.surface -= g_kv * data.get('quantity')
        g_amount.weight -= g_gr * data.get('quantity')

        s_amount = StickerAmount.query.filter_by(type_sticker=data.get('type_product')).first()
        if s_amount.surface < s_kv * data.get('quantity'):
            return jsonify(msg="There isn't enough sticker in warehouse")
        s_amount.surface -= s_kv * data.get('quantity')

        grn_amount = GranulaAmount.query.filter_by(sklad=False).first()
        if s_amount.surface < s_kv * data.get('quantity'):
            return jsonify(msg="There isn't enough granula in warehouse")
        grn_amount.amount -= grn_kg * data.get('quantity')

        db.session.commit()
    except:
        return jsonify(msg='Something went wrong')
    else:
        alyukabond = Alyukabond(
            name = data.get('name'),
            size = data.get('size'),
            type_product = data.get('type_product'),
            sort = data.get('sort'),
            color = data.get('color'),
            list_length = data.get('list_length'),
            list_width = data.get('list_width'),
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
            obj = AluminyAmount.query.filter_by(size = data.get('size'),
                                                type_product = data.get('type_product'),
                                                sort = data.get('sort'),
                                                color = data.get('color'),
                                                list_length = data.get('list_length'),
                                                list_width = data.get('list_width'),
                                                al_thickness = data.get('aluminy_thickness'),
                                                product_thickness = data.get('product_thickness')).first()
            if obj:
                return jsonify(msg='This size already exists')
            else:
                amount = AluminyAmount(size = data.get('size'),
                                        type_product = data.get('type_product'),
                                        sort = data.get('sort'),
                                        color = data.get('color'),
                                        list_length = data.get('list_length'),
                                        list_width = data.get('list_width'),
                                        al_thickness = data.get('aluminy_thickness'),
                                        product_thickness = data.get('product_thickness'),
                                        quantity=0)
                db.session.add(amount)
                db.session.commit()
        amount.quantity += data.get('quantity')
        db.session.commit()
        return jsonify(msg='Success')


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











@bp.route('/create-sale', methods=['GET', 'POST'])
def create_sale():
    if request.method == 'POST':
        data = request.get_json()
        saled = SaledProduct(
        provider = data.get('provider'),
        customer = data.get('customer'),
        agreement_num = data.get('agreement_num'),
        total_price_d = data.get('total_price_d'),
        total_price_s = data.get('total_price_s'),
        payed_price_d = data.get('payed_price_d'),
        payed_price_s = data.get('payed_price_s'),
        debt_d = data.get('debt_d'),
        debt_s = data.get('debt_s'),
        )
        db.session.add(saled)
        db.session.commit()
        return jsonify(msg="Created")
    elif request.method == 'GET':
        sales = SaledProduct.query.all()
        return jsonify(saled_product_schema.dump(sales))
    

