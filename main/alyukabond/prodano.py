from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import  get_jwt_identity, jwt_required
from main.serializers import *
from flask import  jsonify, request
from .utils import *
from .balance import *


# mahsulot sotish
@bp.route('/create-sale', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@jwt_required()
def create_sale():
    user = db.get_or_404(Users, get_jwt_identity())
    if request.method == 'GET':
        id = request.args.get('id')
        agr_num = request.args.get('agreement_number')
        customer = request.args.get('customer')
        saler = request.args.get('saler')
        from_d = request.args.get('from')
        to_d = request.args.get('to')
        if agr_num or agr_num or customer or from_d or to_d or saler:
            data = filter_saled(agr_num=agr_num, customer=customer, saler=saler, from_d=from_d, to_d=to_d)
            return jsonify(data)
        if id is not None:
            products = SaledProduct.query.get(id)
            return jsonify(saled_product_schem.dump(products))
        sales = SaledProduct.query.order_by(SaledProduct.date.desc()).all()
        return jsonify(saled_product_schema.dump(sales))
    elif request.method == 'POST':
        data = request.get_json()
        try:
            saled = SaledProduct(
                driver = data.get('driver'),
                customer = data.get('customer'),
                saler = data.get('saler'),
                agreement_num = data.get('agreement_num'),
                vehicle_number = data.get('vehicle_number'),
                total_price_d = data.get('total_price_d'),
                total_price_s = data.get('total_price_s'),
                payed_price_d = data.get('payed_price_d'),
                payed_price_s = data.get('payed_price_s'),
                debt_d = data.get('debt_d'),
                debt_s = data.get('debt_s'),
                quantity = 0
                )
            db.session.add(saled)
            db.session.flush()
            for product in data.get('products'):    # [{'id':1, 'quantity':1},...]
                prd = db.get_or_404(AlyukabondAmount, product['id'])
                # total_price +=prd.price
                if prd.quantity < product['quantity']:
                    # db.session.delete(saled)
                    # db.session.commit()
                    return jsonify(msg="На складе недостаточно продукт данного типа"), 400
                prd.quantity -= product['quantity']
                saled.quantity += product['quantity']
                selected = SelectedProduct(saled_id=saled.id, product_id=prd.id, quantity=product['quantity'])
                db.session.add(selected)
                db.session.commit()
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
        else:
            balance_add(data.get('payed_price_d'))
            return jsonify(msg="Created")
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            id = request.args.get('id')
            data = request.get_json()
            saled = SaledProduct.query.get(id)
            if saled.editable == True:
                try:
                    extra_sum = float(data.get('payed_price_d', saled.payed_price_d)) - float(saled.payed_price_d)
                    saled.driver = data.get('driver', saled.driver)
                    saled.customer = data.get('customer', saled.customer)
                    saled.saler = data.get('saler', saled.saler)
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
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
            return jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get('id')
            material = db.get_or_404(SaledProduct, id)
            if material.editable == True:
                selected = SelectedProduct.query.filter_by(saled_id=material.id).all()
                for slct in selected:
                    prd = db.get_or_404(AlyukabondAmount, slct.alyukabond.id)
                    prd.quantity += slct.quantity
                db.session.delete(material)
                db.session.commit()
                return jsonify(msg="Deleted")
            return jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401


@bp.route('/nakladnoy-products/<int:id>')
def nakladnoy_products(id):
    products = SelectedProduct.query.filter_by(saled_id=id).all()
    return jsonify(selected_product_schema.dump(products))


# update prodano
@bp.route('/update-saled-products/<int:id>', methods=['PUT'])
@jwt_required()
def update_saled(id):
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == "a":
        if request.method == 'PUT' or request.method == 'PATCH':
            data = request.get_json()
            saled = db.get_or_404(SaledProduct, id)
            if saled.editable == True:
                selecteds = SelectedProduct.query.filter_by(saled_id=saled.id).all()
                lst = selecteds.copy()

                d1_dict = {getattr(obj, 'product_id'):obj for obj in selecteds}
                
                for product in data.get('products'):
                    if product['id'] in d1_dict:
                        prd = db.get_or_404(AlyukabondAmount, product['id'])
                        extra_quantity = product['quantity'] - getattr(d1_dict[product['id']],'quantity')
                        if prd.quantity < extra_quantity:
                            return jsonify(msg="На складе недостаточно алюкобонд данного типа")
                        prd.quantity -= extra_quantity
                        saled.quantity += extra_quantity
                        setattr(d1_dict[product['id']], 'quantity', product['quantity'])
                        lst.remove(d1_dict[product['id']])
                    else:
                        prd = AlyukabondAmount.query.get(product['id'])
                        if prd.quantity < product['quantity']:
                            return jsonify(msg="На складе недостаточно алюкобонд данного типа")
                        prd.quantity -= product['quantity']
                        saled.quantity += product['quantity']
                        s = SelectedProduct(saled_id=saled.id, product_id=prd.id, quantity=product['quantity'])
                        db.session.add(s)
                for s in lst:
                    prd = db.get_or_404(AlyukabondAmount, s['id'])
                    prd.quantity += s.quantity
                    saled.quantity -= s.quantity
                    db.session.delete(s)
                db.session.commit()
                return jsonify(msg="Success")
            return jsonify(msg="Неотредактируемый объект"), 400
    return jsonify(msg="У вас нет полномочий на это действие"), 401

