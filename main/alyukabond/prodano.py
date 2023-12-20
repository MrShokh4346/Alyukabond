from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import  get_jwt_identity, jwt_required
from main.serializers import *
from flask import  jsonify, request
from .utils import *
from .balance import *


# mahsulot sotish
@bp.route('/create-sale', methods=['GET', 'POST', 'PUT', 'PATCH'])
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
        if agr_num or agr_num or customer or from_d or to_d:
            data = filter_saled(agr_num=agr_num, customer=customer, saler=saler, from_d=from_d, to_d=to_d)
            return jsonify(data)
        if id is not None:
            products = SelectedProduct.query.filter_by(saled_id=id).all()
            return jsonify(selected_product_schema.dump(products))
        sales = SaledProduct.query.all()
        return jsonify(saled_product_schema.dump(sales))
    elif request.method == 'POST':
        data = request.get_json()
        try:
            saled = SaledProduct(
                driver = data.get('driver'),
                customer = data.get('customer'),
                saler = data.get('saler'),
                agreement_num = data.get('agreement_num'),
                total_price_d = data.get('total_price_d'),
                total_price_s = data.get('total_price_s'),
                payed_price_d = data.get('payed_price_d'),
                payed_price_s = data.get('payed_price_s'),
                debt_d = data.get('debt_d'),
                debt_s = data.get('debt_s')
                )
            db.session.add(saled)
            # db.session.commit()
            for product in data.get('products'):   # [{'id':1, 'quantity':1},...]
                prd = db.get_or_404(AlyukabondAmount, product['id'])
                # total_price +=prd.price
                if prd.quantity < product['quantity']:
                    # db.session.delete(saled)
                    # db.session.commit()
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
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role == 'a':
            id = request.args.get('saled_id')
            data = request.get_json()
            saled = SaledProduct.query.get(id)
            extra_sum = data.get('payed_price_s', saled.payed_price_s) - saled.payed_price_s
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
        return jsonify("You have not authority to this action"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            material = db.get_or_404(SaledProduct, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify("You have not authority to this action"), 401


# update prodano
@bp.route('/update-saled-products/<int:id>', methods=['PUT'])
@jwt_required()
def update_saled(id):
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == "a":
        if request.method == 'PUT' or request.method == 'PATCH':
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
            db.session.commit()
        return jsonify(msg="Success")
    return jsonify("You have not authority to this action"), 401

