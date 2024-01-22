from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.serializers import *
from flask import  jsonify, request
from .utils import *
from .balance import *
from sqlalchemy import update


# alc_kg, alc_kg_s = 1.4, 5.922   # alyuminiy rangli kg
# al_kv = 3                       # alyuminiy kv
# g_gr, g_gr_s = 270, 1.2906     # kley gr
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
        # color2 = 1 if color2 is None else color2
        thkn = request.args.get("thickness")
        sort = request.args.get("sort")
        length = request.args.get("length")
        if color1 or color2 or thkn or from_d or to_d:
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
                    provider = data.get('provider'),
                    surface = data.get('list_length') * data.get('list_width') * data.get('quantity')
                )                    
                db.session.add(alyukabond)
                db.session.commit()
                # add_alyukabond_amount(type=turi, type_product=data.get('type_product'), color1=rangi1, color2=rangi2, sort=sort, length=data.get('list_length'), al_thickness=qalinligi, product_thickness=data.get('product_thickness'), quantity=miqdor)
                return jsonify(msg='Success')
            else:
                return jsonify(msg=msg)
        except AssertionError as err:
            return jsonify(msg=f"{str(err)}"), 400
    elif request.method == 'PUT' or request.method == 'PATCH':
        if user.role in ['a']:
            id = request.args.get("material_id")
            material = db.get_or_404(Alyukabond, id)
            if material.editable == True:
                try:
                    dct = dict(material.__dict__)
                    del dct["_sa_instance_state"], dct["date"], dct["surface"], dct["id"], dct["editable"]
                    data = request.get_json()
                    if 'size' in data:
                        del data['size']
                    color2 = 1 if data.get('type_product')==1 else data.get('color2_id')
                    data['color2_id'] = color2

                    aluminy1 = AluminyAmount.query.filter_by(color_id=material.color1_id, thickness=material.al_thickness).first()
                    aluminy2 = AluminyAmount.query.filter_by(color_id=material.color2_id, thickness=material.al_thickness).first()
                    glue = GlueAmount.query.filter_by(index1=True).first()
                    sticker = StickerAmount.query.filter_by(type_sticker=material.type_sticker).first()
                    granula = GranulaAmount.query.filter_by(sklad=False).first()

                    old_aluminy_weight = 1.4 * material.quantity
                    old_aluminy_surface = (material.list_width + 0.02) * material.list_length * material.quantity
                
                    aluminy1.weight += old_aluminy_weight
                    aluminy1.surface += old_aluminy_surface

                    aluminy2.weight += old_aluminy_weight
                    aluminy2.surface += old_aluminy_surface

                    old_glue_weight = 270 * material.quantity
                    old_glue_surface = material.list_length * (material.list_width + 0.06) * material.quantity

                    glue.weight += old_glue_weight
                    glue.surface += old_glue_surface
                    glue_check = glue.surface

                    old_sticker_surface = material.list_length * (material.list_width + 0.02) * material.quantity
                    sticker.surface += old_sticker_surface

                    old_granula_weight = 10.3 * material.quantity
                    granula.weight += old_granula_weight
                    grn_check = granula.weight
                    
                    new_aluminy_surface = (data.get("width", material.list_width) + 0.02) * data.get("list_length") * data.get("quantity")
                    new_sticker_surface = (data.get("width", material.list_width) + 0.02) * data.get("list_length") * data.get("quantity")
                    new_glue_surface = (data.get("width", material.list_width) + 0.06) * data.get("list_length") * data.get("quantity")
                    new_granula_weight = 10.3 * data.get("quantity")

                    aluminy1_new = AluminyAmount.query.filter_by(color_id=data.get("color1_id"), thickness=data.get("al_thickness")).first()
                    aluminy2_new = AluminyAmount.query.filter_by(color_id=color2, thickness=data.get("al_thickness")).first()
                    sticker_new = StickerAmount.query.filter_by(type_sticker=data.get("type_sticker")).first()
                    for i in (("алюмина", aluminy1_new), ("алюмина", aluminy2_new), ("наклейка", sticker_new)):
                        if i[1] is None:
                            return jsonify(msg = f"На складе недостаточно {i[0]} данного типа"), 400
                    check_aluminy1_surface = aluminy1_new.surface + old_aluminy_surface if aluminy1_new == aluminy1 else aluminy1_new.surface
                    check_aluminy2_surface = aluminy2_new.surface + old_aluminy_surface if aluminy1_new == aluminy1 else aluminy2_new.surface
                    check_sticker_surface = sticker_new.surface + old_sticker_surface if sticker_new == sticker else sticker_new.surface

                    for i in [("алюмина", check_aluminy1_surface, new_aluminy_surface), ("алюмина", check_aluminy2_surface, new_aluminy_surface), ("наклейка", check_sticker_surface, new_sticker_surface), ("клея", glue_check, new_glue_surface), ("гранула", grn_check, new_granula_weight)]:
                        if i[1] < i[2] :
                            return jsonify( msg = f"На складе недостаточно {i[0]} данного типа"), 400
                            

                    new_alunimy_weight = 1.4 * data.get("quantity")
                    new_glue_weight = 270 * data.get("quantity")
                    
                    aluminy1_new.weight -= new_alunimy_weight
                    aluminy1_new.surface -= new_aluminy_surface
                    aluminy2_new.weight -= new_alunimy_weight
                    aluminy2_new.surface -= new_aluminy_surface
                    glue.weight -= new_glue_weight
                    glue.surface -= new_glue_surface
                    sticker_new.surface -= new_sticker_surface
                    granula.weight -= new_granula_weight
                    # print(aluminy2.__dict__)

                    db.session.commit()
                    difference = dict(data.items() ^ dct.items())
                    update_record = {}
                    for key, value in difference.items():
                        update_record[key] = data[key] 
                    if update_record:
                        stmt = update(Alyukabond).where(Alyukabond.id == id).values(**update_record)
                        db.session.execute(stmt)
                        db.session.commit()
                    return jsonify(msg="Success")
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
            return jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401
    elif request.method == 'DELETE':
        if user.role == 'a':
            id = request.args.get('material_id')
            material = db.get_or_404(Alyukabond, id)
            if material.editable == True:
                aluminy1 = AluminyAmount.query.filter_by(color_id=material.color1_id, thickness=material.al_thickness).first()
                aluminy2 = AluminyAmount.query.filter_by(color_id=material.color2_id, thickness=material.al_thickness).first()
                aluminy1.weight += 1.4 * material.quantity
                aluminy1.surface += (material.list_width + 0.02) * material.list_length * material.quantity
                aluminy2.weight += 1.4 * material.quantity
                aluminy2.surface += (material.list_width + 0.02) * material.list_length * material.quantity
                glue = GlueAmount.query.filter_by(index1=True).first()
                glue.weight += 270 * material.quantity
                glue.surface += material.list_length * (material.list_width + 0.06) * material.quantity
                sticker = StickerAmount.query.filter_by(type_sticker=material.type_sticker).first()
                sticker.surface +=  material.list_length * (material.list_width + 0.02) * material.quantity
                granula = GranulaAmount.query.filter_by(sklad=False).first()
                granula.weight += 10.3 * material.quantity
                db.session.delete(material)
                db.session.commit()
                return jsonify(msg="Deleted")
            return jsonify(msg="Неотредактируемый объект"), 400
        return jsonify(msg="У вас нет полномочий на это действие"), 401

