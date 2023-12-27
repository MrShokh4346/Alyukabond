from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.serializers import *
from flask import  jsonify, request
from .utils import *
from .balance import *


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
        material_id = request.args.get("material_id")
        from_d = request.args.get("from")
        to_d = request.args.get("to") 
        color1 = request.args.get("color1")
        color2 = request.args.get("color2")
        color2 = 1 if color2 is None else color2
        thkn = request.args.get("thickness")
        sort = request.args.get("sort")
        length = request.args.get("length")
        if color1 or thkn or from_d or to_d:
            data = filter_amount(name="alyukabond", sort=sort, thickness=thkn, color1=color1, color2=color2,from_d=from_d, to_d=to_d, length=length)
            return jsonify(data)
        if material_id is not None:
            return jsonify(alyukabond_schema.dump(Alyukabond.query.get_or_404(material_id)))
        alyukabonds = Alyukabond.query.order_by(Alyukabond.date.desc()).all()
        return jsonify(alyukabond_schemas.dump(alyukabonds))
    elif request.method == 'POST':
        try:
            data = request.get_json()
            turi = data.get('type_sticker')
            rangi1 = data.get('color1_id')
            rangi2 = data.get('color2_id', None)
            qalinligi = data.get('al_thickness')
            length = data.get('list_length') 
            width = data.get('list_width', 1.22)
            sort = request.get_json().get('sort')
            miqdor = request.get_json().get('quantity')
            rangi2 = 1 if data.get('type_product') == 1 else rangi2
            msg = check(turi=turi, rangi1=rangi1, rangi2=rangi2, qalinligi=qalinligi, length=length, width=width, miqdor=miqdor)
            if msg == 'success':
                alyukabond = Alyukabond(
                    name = data.get('name'),
                    size = data.get('size'),
                    type_product = data.get('type_product'),
                    type_sticker = data.get('type_sticker'),
                    sort = data.get('sort'),
                    color1_id = data.get('color1_id'),
                    color2_id = rangi2,
                    list_length = data.get('list_length'),
                    list_width = data.get('list_width'),
                    al_thickness = data.get('al_thickness'),
                    product_thickness = data.get('product_thickness'),
                    quantity = data.get('quantity'),
                    provider = data.get('provider')
                )                    
                db.session.add(alyukabond)
                db.session.commit()
                add_alyukabond_amount(type=turi, type_product=data.get('type_product'), color1=rangi1, color2=rangi2, sort=sort, length=data.get('list_length'), al_thickness=qalinligi, product_thickness=data.get('product_thickness'), quantity=miqdor)
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
                update_alyukabond_amount(material=material, type=data.get('type_sticker', material.type_sticker), sort=data.get('sort', material.sort), color1=data.get('color1', material.color1),
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
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get('material_id')
            material = db.get_or_404(Alyukabond, id)
            db.session.delete(material)
            db.session.commit()
            return jsonify(msg="Deleted")
        return jsonify(msg="У вас нет полномочий на это действие"), 401

