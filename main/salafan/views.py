from flask import jsonify, request, redirect, url_for
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from main.salafan import bp
from main.models import *
from main import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from main.serializers import *
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import  send_from_directory, url_for, jsonify, request
from uuid import uuid1
import os


# xomashyo malumot kiritish
@bp.route('/material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        if id is not None:
            material =  db.get_or_404(GranulaMaterial, id)
            return jsonify(material_schema.dump(material))
        g_materials = GranulaMaterial.query.all()
        return jsonify(material_schemas.dump(g_materials))
    elif request.method == 'POST':
        if user.role == 'a':
            material = GranulaMaterial(
                name = request.get_json().get('name'),
                type_material = request.get_json().get('type_material'),
                total_weight = request.get_json().get('total_weight'),
                waste = request.get_json().get('waste'),
                weight = round(float(request.get_json().get('total_weight')) * (1 - float(request.get_json().get('waste')) / 100), 2),
                price_per_kg = request.get_json().get('price_per_kg'),
                total_price = request.get_json().get('total_price'),
                payed_price = request.get_json().get('payed_price'),
                debt = round(float(request.get_json().get('total_price')) - float(request.get_json().get('payed_price')), 2),
                provider = request.get_json().get('provider'),
                status = request.get_json().get('status')
            )
            db.session.add(material)
            db.session.commit()
            material_amount = MaterialAmount.query.filter_by(index1=True).first()
            if not material_amount:
                material_amount = MaterialAmount(amount=0, index1=True)
                db.session.add(material_amount)
                db.session.commit()
            material_amount.amount += material.weight
            db.session.commit()
            return jsonify(msg="Success"), 201
        return jsonify("You are not admin"), 401
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            material = GranulaMaterial.query.get(id)
            material.name = request.get_json().get('name', material.name)
            material.type_material = request.get_json().get('type_material', material.type_material)
            material.total_weight = request.get_json().get('total_weight', material.total_weight)
            material.waste = request.get_json().get('waste', material.waste)
            material.weight = round(float(material.total_weight) * (1 - float(material.waste) / 100), 2)
            material.price_per_kg = request.get_json().get('price_per_kg', material.price_per_kg)
            material.total_price = request.get_json().get('total_price', material.total_price)
            material.payed_price = request.get_json().get('payed_price', material.payed_price)
            material.debt = round(float(material.total_price) - float(material.payed_price), 2)
            material.provider = request.get_json().get('provider', material.provider)
            db.session.commit()
            return jsonify(msg='Success')
        return jsonify("You are not admin"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(GranulaMaterial, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You are not admin"), 401


# setka malumot kititish
@bp.route('/setka', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def setka():
    id = request.args.get('setka_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        setka = Setka(setka_type=request.get_json().get('type'), bulk=request.get_json().get('hajm'))
        db.session.add(setka)
        db.session.commit()
        return jsonify(msg="Created")
    elif request.method == 'GET':
        setka = db.session.execute(db.select(Setka).order_by(Setka.date.desc())).scalars()
        return jsonify(setka_schemas.dump(setka))
    elif request.method == 'DELETE':
        if user.role == 'a':
            setka = db.get_or_404(Setka, id)
            db.session.delete(setka)
            db.session.commit()
            return jsonify(msg = 'Deleted')
        return jsonify("You are not admin"), 401


# qarzni boshqarish
@bp.route('/debt')
@jwt_required()
def debt():
    user = db.get_or_404(Users, get_jwt_identity())
    data = {"materials":[]}
    total_sum = 0
    total_payed = 0
    total_debt = 0
    if user.role == 'a':
        data['materials'].append(material_schemas.dump(GranulaMaterial.query.all()))
        data['total'] = {
            "total_sum":GranulaMaterial.query.with_entities(func.sum(GranulaMaterial.total_price)).all()[0][0],
            "total_debt":GranulaMaterial.query.with_entities(func.sum(GranulaMaterial.debt)).all()[0][0],
            "total_payed":GranulaMaterial.query.with_entities(func.sum(GranulaMaterial.payed_price)).all()[0][0],
        }
        return jsonify(data)
    return jsonify(msg="You are not admin"), 401


# xisobot
@bp.route('/report')
@jwt_required()
def report():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        granula_amount = GranulaAmount.query.filter_by(sklad=False).first()

        data = {
            "poterya":GranulaSklad.query.with_entities(func.sum(GranulaSklad.material_weight - GranulaSklad.granula_weight)).all()[0][0],
            "sklad":granula_amount.weight if granula_amount else "There isn't granula in the warehouse",
            ###"обород"
        }
        return jsonify(data)
    return jsonify(msg="You are not admin"), 401


# rasxod
@bp.route('/expence', methods=['POST', 'GET'])
def expence():
    if request.method == 'POST':
        exp = Expence(
            description = request.get_json().get('description'),
            user = request.get_json().get('user'),
            price = request.get_json().get('price')
        )
        db.session.add(exp)
        db.session.commit()
        return jsonify(msg='Created')
    else:
        exp = Expence.query.all()
        return jsonify(expence_schema.dump(exp))


# # asosoiy sexga utkazish
# @bp.route('/move-to-main', methods=['POST'])
# def move_to_main():
#     amount = float(request.get_json().get('amount'))
#     granula_sklad = GranulaAmount.query.filter_by(sklad=True).first()
#     granula_main = GranulaAmount.query.filter_by(sklad=False).first()
#     if amount and (amount < granula_sklad.amount):
#         granula_sklad.amount -= amount
#         granula_main.amount += amount
#         db.session.commit()
#         return jsonify(msg="Success")
#     return jsonify(msg="There are no such amount product")


# sklad
@bp.route('/warehouse')
def warehouse():
    data = {}
    m_a = MaterialAmount.query.filter_by(index1=True).first()
    g_a = GranulaAmount.query.filter_by(sklad=False).first()
    data['material_amount'] = m_a.amount if m_a else "There isn't material in the warehouse"
    data['granula_amount'] = g_a.weight if g_a else "There isn't granula in the warehouse"
    return jsonify(data)


# granula sklad
@bp.route('/make-granula', methods=['GET', "POST"])
def make_granula():
    data = request.get_json()
    if request.method == 'POST':
        granula = GranulaSklad(
            material_weight = data.get("material_weight"),
            granula_weight = data.get("granula_weight"),##################### poteriya, provider
            provider = data.get('provider'),
            poteriya = data.get("material_weight") - data.get("granula_weight")
        )
        db.session.add(granula)
        amount = GranulaAmount.query.filter_by(sklad=False).first()
        if not amount:
            amount = GranulaAmount(weight=0)
            db.session.add(amount)
        amount.weight += data.get("granula_weight")
        db.session.commit()
        return jsonify(msg="Success")
    else:
        data = {
            'granulas':gr_sklad_schema.dump(GranulaSklad.query.all()),
            'amount':gr_amount_schema.dump(GranulaAmount.query.filter_by(sklad=False).first())
        }
        return jsonify(data)