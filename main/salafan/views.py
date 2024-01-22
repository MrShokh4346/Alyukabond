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
from .balance import balance_add, balance_minus
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
            g_materials = GranulaMaterial.query.filter(GranulaMaterial.date.between(d, s)).order_by(GranulaMaterial.date.desc()).all()
            return jsonify(material_schemas.dump(g_materials))
        if id is not None:
            material =  db.get_or_404(GranulaMaterial, id)
            return jsonify(material_schema.dump(material))
        g_materials = GranulaMaterial.query.order_by(GranulaMaterial.date.desc()).all()
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
                price_per_kg_s = round(float(request.get_json().get('price_per_kg_s')), 2),
                total_price_d = round(float(request.get_json().get('total_price_d')), 2),
                payed_price_d = round(float(request.get_json().get('payed_price_d')), 2),
                debt_d = round(float(request.get_json().get('debt_d')), 2),
                total_price_s = round(float(request.get_json().get('total_price_s')), 2),
                payed_price_s = round(float(request.get_json().get('payed_price_s')), 2),
                debt_s = round(float(request.get_json().get('debt_s')), 2),
                provider = request.get_json().get('provider')
            )
            db.session.add(material)
            balance_minus(material.payed_price_d)
            db.session.commit()
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
        return jsonify(msg="Success"), 201
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a', 'se']:
            material = GranulaMaterial.query.get(id)
            if material.editable == True:
                try:
                    extra_sum = request.get_json().get('payed_price_d', material.payed_price_d) - material.payed_price_d
                    material.name = request.get_json().get('name', material.name)
                    material.type_material = request.get_json().get('type_material', material.type_material)
                    material.total_weight = request.get_json().get('total_weight', material.total_weight)
                    material.waste = request.get_json().get('waste', material.waste)
                    material.weight = request.get_json().get('weight', material.weight)
                    material.price_per_kg = request.get_json().get('price_per_kg', material.price_per_kg)
                    material.price_per_kg_s = request.get_json().get('price_per_kg_s', material.price_per_kg_s)
                    material.total_price_d = round(float(request.get_json().get('total_price_d', material.total_price_d)), 2)
                    material.payed_price_d = round(float(request.get_json().get('payed_price_d', material.payed_price_d)), 2)
                    material.debt_d = round(float(request.get_json().get('debt_d', material.debt_d)), 2)
                    material.total_price_s = round(float(request.get_json().get('total_price_s', material.total_price_s)), 2)
                    material.payed_price_s = round(float(request.get_json().get('payed_price_s', material.payed_price_s)), 2)
                    material.debt_s = round(float(request.get_json().get('debt_s', material.debt_s)), 2)
                    material.provider = request.get_json().get('provider', material.provider)
                    db.session.commit()
                    balance_minus(extra_sum)
                    return jsonify(msg='Success')
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
            return jsonify(msg="Неотредактируемый объект"), 400 
        return jsonify("У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(GranulaMaterial, id)
            if material.editable == True:
                balance_add(material.payed_price_d)
                db.session.delete(material)
                db.session.commit()
                return jsonify(msg="Deleted")
            return jsonify(msg="Неотредактируемый объект"), 400 
        return jsonify("У вас нет полномочий на это действие"), 401


# setka malumot kititish
@bp.route('/setka', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def setka():
    id = request.args.get('setka_id')
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        if user.role in ['a', 'se']:
            setka = Setka(setka_type=request.get_json().get('type_material'), bulk=request.get_json().get('hajm'))
            db.session.add(setka)
            db.session.commit()
            return jsonify(msg="Created")
        return jsonify(msg='У вас нет полномочий на это действие'), 401
    if request.method == 'PUT':
        if user.role in ['a']:
            setka = Setka.query.get(id)
            if setka.editable == True:
                setka.setka_type = request.get_json().get('type_material') 
                setka.bulk = request.get_json().get('hajm')
                db.session.commit()
                return jsonify(msg="Success")
            return jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg='У вас нет полномочий на это действие'), 401
    elif request.method == 'GET':
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        setka_type = request.args.get("setka_type")
        query = f"SELECT * FROM setka WHERE"   
        query += f" setka_type='{setka_type}' AND" if setka_type is not None else ''
        if (from_d and to_d):
            query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
        query = query[:-4]
        query += " ORDER BY date DESC" 
        prds = db.session.execute(text(query)).fetchall()
        if id is not None:
            setka = Setka.query.get(id)
            return jsonify(setka_schema.dump(setka))
        return jsonify(setka_schemas.dump(prds))
    elif request.method == 'DELETE':
        if user.role == 'a':
            setka = db.get_or_404(Setka, id)
            if setka.editable == True:
                db.session.delete(setka)
                db.session.commit()
                return jsonify(msg = 'Deleted')
            return jsonify(msg="Неотредактируемый объект"), 400
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


# rasxod
@bp.route('/expence', methods=['POST', 'GET'])
@jwt_required()
def expence():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        try:
            exp = Expence(
            description = request.get_json().get('description'),
            user = request.get_json().get('user'),
            status = request.get_json().get('status'),
            seb = request.get_json().get('seb'),
            price = round(float(request.get_json().get('price')), 2),
            price_s = round(float(request.get_json().get('price_s')), 2)
            )
            db.session.add(exp)
            balance_minus(exp.price)
            db.session.commit()
            return jsonify(msg='Created')
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'GET':
        status = request.args.get('status')
        if status=='undefined':
            status = None
        seb = request.args.get('seb')
        if seb=='undefined':
            seb = None
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        query = f"SELECT * FROM expence WHERE "   
        query += f"seb='{seb}' AND" if seb is not None else ''
        query += f" status='{status}' AND" if status is not None else ''
        if (from_d and to_d):
            query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
        query = query[:-4]
        query += " ORDER BY date DESC"
        prds = db.session.execute(text(query)).fetchall()
        return jsonify(expence_schema.dump(prds))
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
    name = request.args.get('name')
    if name is not None:
        salafan = MaterialAmount.query.filter_by(index1=True).first()
        return jsonify([material_amount_schema.dump(salafan)])
    g_a = GranulaAmount.query.filter_by(sklad=False).first()
    return jsonify([{"weight":g_a.weight if g_a else 0}])


# granula sklad
@bp.route('/make-granula', methods=['GET', "POST", "PUT", "PATCH", 'DELETE'])
@jwt_required()
def make_granula():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'POST':
        data = request.get_json()
        material = MaterialAmount.query.filter_by(index1=True).first()
        if (material.amount >= data.get("material_weight")) and data.get("material_weight")>0:
            material.amount -= data.get("material_weight")
            if data.get("material_weight") - data.get("granula_weight") > 0:
                granula = GranulaPoteriya(
                    material_weight = data.get("material_weight"),
                    granula_weight = data.get("granula_weight"),
                    provider = data.get('provider'),
                    poteriya = data.get("material_weight") - data.get("granula_weight")
                )
            else:
                return jsonify(msg="Гранула не может быть больше материала"), 400
            db.session.add(granula)
            db.session.commit()
            return jsonify(msg="Success")
        else:
            return jsonify(msg="На складе недостаточно материал"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            data = request.get_json()
            id = request.args.get("id")
            granula = db.get_or_404(GranulaPoteriya, id)
            if granula.editable == True:
                material = MaterialAmount.query.filter_by(index1=True).first()
                granula.provider = data.get('provider')
                extra =  data.get("material_weight") - granula.material_weight 
                if material.amount >= extra:
                    if data.get("material_weight") - data.get("granula_weight") > 0:
                        material.amount -= extra
                        granula.material_weight = data.get("material_weight")
                        granula.granula_weight = data.get("granula_weight")
                        granula.poteriya = data.get("material_weight") - data.get("granula_weight")
                        db.session.commit()
                        return jsonify(msg="Success")
                    return jsonify(msg="Гранула не может быть больше материала"), 400
                return jsonify(msg="На складе недостаточно материал"), 400
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get('id')
            poteriya = db.get_or_404(GranulaPoteriya, id)
            material = MaterialAmount.query.filter_by(index1=True).first()
            if poteriya.editable == True:
                material.amount += poteriya.material_weight
                db.session.delete(poteriya)
                db.session.commit()
                return jsonify(msg="Deleted")
            return  jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'GET':
        id = request.args.get('id')
        from_d = request.args.get("from")
        to_d = request.args.get("to")
        if from_d and to_d:
            query = f"SELECT * FROM granula_poteriya WHERE date BETWEEN '{from_d}' AND '{to_d}' ORDER BY date DESC"
            prds = db.session.execute(text(query)).fetchall()
            return jsonify(gr_sklad_schema.dump(prds))
        if id is not None:
            return jsonify(gr_sklad_schem.dump(GranulaPoteriya.query.get(id)))
        return jsonify(gr_sklad_schema.dump(GranulaPoteriya.query.order_by(GranulaPoteriya.date.desc()).all()))
