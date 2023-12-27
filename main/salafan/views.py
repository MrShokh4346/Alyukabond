from flask import jsonify, request, redirect, url_for
from datetime import datetime, timedelta, timezone
from flask import Blueprint
from main.models import *
from main import jwt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, get_jwt
from main.serializers import *
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
from flask import  send_from_directory, url_for, jsonify, request
from uuid import uuid1
import os
from .balance import balance_minus
from main.salafan import bp
from sqlalchemy import text



# xomashyo malumot kiritish
@bp.route('/material', methods=['GET', "POST", 'PATCH', 'PUT', 'DELETE'])
@jwt_required()
def material():
    id = request.args.get('material_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            from_d, to_d = from_d.split('-'), to_d.split('-')
            d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
            s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
            g_materials = GranulaMaterial.query.filter(GranulaMaterial.date.between(d, s)).all()
            return jsonify(material_schemas.dump(g_materials))
        if id is not None:
            material =  db.get_or_404(GranulaMaterial, id)
            return jsonify(material_schema.dump(material))
        g_materials = GranulaMaterial.query.all()
        return jsonify(material_schemas.dump(g_materials))
    elif request.method == 'POST':
        try:
            material = GranulaMaterial(
                name = request.get_json().get('name'),
                type_material = request.get_json().get('type_material'),
                total_weight = request.get_json().get('total_weight'),
                waste = request.get_json().get('waste'),
                weight = request.get_json().get('weight'),
                price_per_kg = request.get_json().get('price_per_kg'),
                price_per_kg_s = request.get_json().get('price_per_kg_s'),
                total_price_d = request.get_json().get('total_price_d'),
                payed_price_d = request.get_json().get('payed_price_d'),
                debt_d = request.get_json().get('debt_d'),
                total_price_s = request.get_json().get('total_price_s'),
                payed_price_s = request.get_json().get('payed_price_s'),
                debt_s = request.get_json().get('debt_s'),
                provider = request.get_json().get('provider'),
                status = request.get_json().get('status')
            )
            db.session.add(material)
            balance_minus(material.payed_price_d)
            db.session.commit()
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
        material_amount = MaterialAmount.query.filter_by(index1=True).first()
        if not material_amount:
            material_amount = MaterialAmount(amount=0, index1=True)
            db.session.add(material_amount)
            db.session.commit()
        material_amount.amount += material.weight
        db.session.commit()
        return jsonify(msg="Success"), 201
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            try:
                material = GranulaMaterial.query.get(id)
                extra_sum = request.get_json().get('payed_price', material.payed_price) - material.payed_price
                material.name = request.get_json().get('name', material.name)
                material.type_material = request.get_json().get('type_material', material.type_material)
                material.total_weight = request.get_json().get('total_weight', material.total_weight)
                material.waste = request.get_json().get('waste', material.waste)
                material.weight = round(float(material.total_weight) * (1 - float(material.waste) / 100), 2)
                material.price_per_kg = request.get_json().get('price_per_kg', material.price_per_kg)
                material.price_per_kg_s = request.get_json().get('price_per_kg_s', material.price_per_kg_s)
                material.total_price_d = request.get_json().get('total_price_d', material.total_price_d)
                material.payed_price_d = request.get_json().get('payed_price_d', material.payed_price_d)
                material.debt_d = request.get_json().get('debt_d', material.debt_d)
                material.total_price_s = request.get_json().get('total_price_s', material.total_price_s)
                material.payed_price_s = request.get_json().get('payed_price_s', material.payed_price_s)
                material.debt_s = request.get_json().get('debt_s', material.debt_s)
                material.provider = request.get_json().get('provider', material.provider)
                db.session.commit()
                balance_minus(extra_sum)
                return jsonify(msg='Success')
            except AssertionError as err:
                return jsonify(msg=f"{str(err)}"), 400
        return jsonify("У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(GranulaMaterial, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("У вас нет полномочий на это действие"), 401


# setka malumot kititish
@bp.route('/setka', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def setka():
    id = request.args.get('setka_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        if user.role in ['a', 'se']:
            setka = Setka(setka_type=request.get_json().get('type'), bulk=request.get_json().get('hajm'))
            db.session.add(setka)
            db.session.commit()
            return jsonify(msg="Created")
        return jsonify(msg='У вас нет полномочий на это действие'), 401
    elif request.method == 'GET':
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            from_d, to_d = from_d.split('-'), to_d.split('-')
            d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
            s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
            setka = Setka.query.filter(Setka.date.between(d, s)).all()
            return jsonify(setka_schemas.dump(setka))
        setka = db.session.execute(db.select(Setka).order_by(Setka.date.desc())).scalars()
        return jsonify(setka_schemas.dump(setka))
    elif request.method == 'DELETE':
        if user.role == 'a':
            setka = db.get_or_404(Setka, id)
            db.session.delete(setka)
            db.session.commit()
            return jsonify(msg = 'Deleted')
        return jsonify("У вас нет полномочий на это действие"), 401


# xisobot
@bp.route('/report')
@jwt_required()
def report():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role in ['a', 'se']:
        granula_amount = GranulaAmount.query.filter_by(sklad=False).first()

        data = {
            "poterya":GranulaPoteriya.query.with_entities(func.sum(GranulaPoteriya.material_weight - GranulaPoteriya.granula_weight)).all()[0][0],
            "sklad":granula_amount.weight if granula_amount else "На складе недостаточно гранула",
        }
        return jsonify(data)
    return jsonify(msg="У вас нет полномочий на это действие"), 401


# # client
# @bp.route('/client', methods=['POST', 'GET'])
# @jwt_required()
# def client():
#     if request.method=='GET':
#         cilent = Client.query.all()
#         return jsonify(client_schema.dump(cilent))
#     else:
#         data = request.get_json()
#         cilent = Client(user=data.get('user'))
#         db.session.add(cilent)
#         db.session.commit()
#         return jsonify(msg="Success")


# # rasxod maqsad
# @bp.route('/expence-intent', methods=['POST', 'GET'])
# @jwt_required()
# def expence_intent():
#     if request.method=='GET':
#         exp_intent = ExpenceIntent.query.all()
#         return jsonify(expence_intent_schema.dump(exp_intent))
#     else:
#         data = request.get_json()
#         intent = ExpenceIntent(description=data.get('description'))
#         db.session.add(intent)
#         db.session.commit()
#         return jsonify(msg="Success")


# # rasxod user
# @bp.route('/expence-user', methods=['POST', 'GET'])
# @jwt_required()
# def expence_user():
#     if request.method == 'GET':
#         exp_user = ExpenceUser.query.all()
#         return jsonify(expence_user_schema.dump(exp_user))
#     else:
#         data = request.get_json()
#         user = ExpenceUser(user=data.get('user'))
#         db.session.add(user)
#         db.session.commit()
#         return jsonify(msg="Success")


# rasxod
@bp.route('/expence', methods=['POST', 'GET'])
@jwt_required()
def expence():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        exp = Expence(
            description = request.get_json().get('description'),
            user = request.get_json().get('user'),
            status = request.get_json().get('status'),
            price = request.get_json().get('price'),
            price_s = request.get_json().get('price_s')
        )
        try:
            db.session.add(exp)
            balance_minus(exp.price)
            db.session.commit()
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
        return jsonify(msg='Created')
    elif request.method == 'GET':
        status = request.args.get('status')
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            from_d, to_d = from_d.split('-'), to_d.split('-')
            d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
            s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
            exp = Expence.query.filter(Expence.date.between(d, s), Expence.status==status).all()
            return jsonify(expence_schema.dump(exp))
        exp = Expence.query.filter_by(status=status).all() if status is not None else Expence.query.all()
        return jsonify(expence_schema.dump(exp))
    else:
        if user.role == 'a':
            id = request.args.get('id')
            exp = Expence.query.get(id)
            db.session.delete(exp)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# sklad
@bp.route('/warehouse')
def warehouse():
    data = {}
    g_a = GranulaAmount.query.filter_by(sklad=False).first()
    return jsonify([{"weight":g_a.weight if g_a else 0}])


# granula sklad
@bp.route('/make-granula', methods=['GET', "POST"])
def make_granula():
    if request.method == 'POST':
        data = request.get_json()
        material = MaterialAmount.query.filter_by(index1=True).first()
        if material.amount > data.get("material_weight"):
            material.amount -= data.get("material_weight")
            granula = GranulaPoteriya(
                material_weight = data.get("material_weight"),
                granula_weight = data.get("granula_weight"),
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
            return jsonify(msg="На складе недостаточно материал")
    else:
        id = request.args.get('id')
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            query = f"SELECT * FROM granula_poteriya WHERE date BETWEEN '{from_d}' AND '{to_d}'"
            prds = db.session.execute(text(query)).fetchall()
            return jsonify(gr_sklad_schema.dump(prds))
        if id is not None:
            return jsonify(gr_sklad_schem.dump(GranulaPoteriya.query.get(id)))
        # data = {
        #     'poteriya':gr_sklad_schema.dump(GranulaPoteriya.query.all()),
        #     'amount':gr_amount_schema.dump(GranulaAmount.query.filter_by(sklad=False).first())
        # }
        return jsonify(gr_sklad_schema.dump(GranulaPoteriya.query.all()))