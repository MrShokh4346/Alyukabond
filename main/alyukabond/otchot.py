from datetime import datetime, timedelta, date
from main.alyukabond import bp
from main.models import *
from main import jwt
from flask_jwt_extended import get_jwt_identity, jwt_required
from main.serializers import *
from sqlalchemy.sql import func
from flask import  send_from_directory, jsonify, request
from openpyxl import Workbook, load_workbook
import shutil
from .utils import *
from .balance import *

def salafan_rasxod(frm, to):
    d = to - timedelta(days=30)
    material = GranulaMaterial.query.with_entities(func.avg(GranulaMaterial.price_per_kg)).filter(GranulaMaterial.date.between(d, to)).all()
    granula = GranulaPoteriya.query.with_entities(func.sum(GranulaPoteriya.granula_weight), func.sum(GranulaPoteriya.material_weight)).filter(GranulaPoteriya.date.between(frm, to)).all()
    exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.status=='salafan', Expence.date.between(frm, to)).all()
    rasxod = exp[0][0] if exp[0][0] else 0
    salafan = granula[0][1] if granula[0][1] else 0 
    granula = granula[0][0] if granula[0][0] else 1 
    avg_narx = material[0][0] if material[0][0] else 0 
    salafan_narx = salafan*avg_narx if salafan else 0
    data = {
        "salafan":salafan_narx,
        "grn_rasxod":rasxod
    }
    return data


# sebestoymost
@bp.route('/price')
def alyukabond_price():
    f_date = request.args.get('from')
    t_date = request.args.get('to')
    from_d = f_date.split('-')
    to_d = t_date.split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    color1 = request.args.get('color1')
    color2 = request.args.get('color2')
    thkn = float(request.args.get('al_thickness', 0))
    typ = int(request.args.get('type', 0))
    length = request.args.get('length', 0)
    grn_price = salafan_rasxod(frm=d, to=s)
    rate = ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
    query = f"select sum(quantity) from alyukabond where color1_id='{color1}' and color2_id='{color2}' and al_thickness='{thkn}' and list_length='{length}' and date between '{f_date}' and '{t_date}'"
    alyukabond_quantity = db.session.execute(text(query)).fetchall()
    aluminy_color1 = Aluminy.query.with_entities(func.sum(Aluminy.price)).filter(Aluminy.color_id==color1, Aluminy.thickness==thkn, Aluminy.date.between(d, s)).all()
    aluminy_color2 = Aluminy.query.with_entities(func.sum(Aluminy.price)).filter(Aluminy.color_id==color2, Aluminy.thickness==thkn, Aluminy.date.between(d, s)).all()
    glue = Glue.query.with_entities(func.sum(Glue.total_price_d)).filter(Glue.date.between(d, s)).all()
    sticker = Sticker.query.with_entities(func.sum(Sticker.price)).filter(Sticker.type_sticker==typ, Sticker.date.between(d, s)).all()
    exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.status!='salafan', Expence.date.between(d, s)).all()
    r = exp[0][0] / rate.rate if exp[0][0] else 0
    al1 =  aluminy_color1[0][0] if aluminy_color1[0][0] else 0
    al2 = aluminy_color2[0][0] if aluminy_color2[0][0] else 0
    gl =  glue[0][0] if glue[0][0] else 0
    st = sticker[0][0] if sticker[0][0] else 0
    grn =  (grn_price["salafan"] / rate.rate)
    quantity_alyukabond = alyukabond_quantity[0][0] if alyukabond_quantity[0][0] else 0
    sebistoymost = (al1 + al2 + gl + st + grn + r) / quantity_alyukabond 
    data = {
        "aluminy_color1":al1,
        "aluminy_color2":al2,
        "glue":gl,
        "sticker":st,
        "salafan":grn,
        "rasxod_salafan":grn_price["grn_rasxod"] / rate.rate,
        "rasxod_alyukabond":r,
        "quantity_alyukabond":quantity_alyukabond,
        "sebistoymost":sebistoymost
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
            salafan = GranulaMaterial.query.filter(GranulaMaterial.date.between(d, s)).all()
            data = {
                "aluminy":aluminy_schemas.dump(aluminy),
                "glue":glue_schemas.dump(glue),
                "sticker":sticker_schemas.dump(sticker),
                "salafan":salafan_schema.dump(salafan)
            }
        else:
            objects = {
                "aluminy":aluminy_schemas.dump(Aluminy.query.filter(Aluminy.date.between(d, s)).all()),
                "glue":glue_schemas.dump(Glue.query.filter(Glue.date.between(d, s)).all()),
                "sticker":sticker_schemas.dump(Sticker.query.filter(Sticker.date.between(d, s)).all()),
                "salafan":salafan_schema.dump(GranulaMaterial.query.filter(GranulaMaterial.date.between(d, s)).all())
            }.get(fr, None)
            data = {f"{fr}":objects}
        return jsonify(data)
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


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
        return jsonify(alyukabond_schemas.dump(alyukabond))
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


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
        saled = SaledProduct.query.filter(SaledProduct.date.between(d, s)).all()
        data = {
            "saled":saled_product_schema.dump(saled)
        }
        return jsonify(data)
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# Qarzlar xisobot
@bp.route('/report/debt', methods=['GET', 'POST'])
@jwt_required()
def report_debt():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        if request.method == 'GET':
            from_d = request.args.get('from')
            to_d = request.args.get('to')
            partiya = request.args.get('partiya')
            provider = request.args.get('provider')
            fr = request.args.get('filter', None)
            aluminy = filter_nakladnoy(name="aluminy_nakladnoy", partiya=partiya, provider=provider, from_d=from_d, to_d=to_d) if fr=='aluminy' else None
            glue = glue_schemas.dump(Glue.query.filter(Glue.date > from_d, Glue.date < to_d).all()) if fr=='glue' else None
            sticker = filter_nakladnoy(name="sticker_nakladnoy", partiya=partiya, provider=provider, from_d=from_d, to_d=to_d) if fr=='sticker' else None
            salafan = salafan_schema.dump(GranulaMaterial.query.filter(GranulaMaterial.date > from_d, GranulaMaterial.date < to_d).all()) if fr=='salafan' else None
            data = {
                "aluminy":aluminy,
                "sticker":sticker,
                "glue":glue,
                "salafan":salafan
            }.get(fr, None)
            return jsonify(data)
        elif request.method == 'POST':
            id = request.args.get('id')
            name = request.args.get('name')
            data = request.get_json()
            material = {
                "aluminy":AluminyNakladnoy.query.get(id),
                "sticker":StickerNakladnoy.query.get(id),
                "glue":Glue.query.get(id),
                "salafan":GranulaMaterial.query.get(id)
            }.get(name, None)
            debt = material.debt_s if name != 'salafan' else material.debt
            if debt >= data.get('amount_s'):
                if name != 'salafan':
                    material.total_price_s = material.total_price_s
                    material.total_price_d = material.total_price_d
                    material.payed_price_d += data.get('amount_d')
                    material.payed_price_s += data.get('amount_s')
                    material.debt_d -= data.get('amount_d')
                    material.debt_s -= data.get('amount_s')
                else:
                    material.total_price = material.total_price
                    material.payed_price += data.get('amount_s')
                    material.debt -= data.get('amount_s') 
                payed = {
                    'aluminy':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), aluminy_nakladnoy_id = material.id),
                    'glue':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), glue_id = material.id),
                    'sticker':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), sticker_nakladnoy_id = material.id),
                    'salafan':PayedDebt(amount_s=data.get('amount_s'), user=data.get('user'), salafan_id = material.id)
                }.get(name, None)
                db.session.add(payed)
                db.session.commit()
                balance_minus(data.get('amount_d'))
                return jsonify(msg="Success")
            return jsonify(msg="You are entered more then debt")
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# Haqlar xisobot
@bp.route('/report/fee', methods=['GET', 'POST'])
@jwt_required()
def report_fee():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        if request.method == 'GET':
            from_d = request.args.get('from').split('-')
            to_d = request.args.get('to').split('-')
            d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
            s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
            alyukabond = SaledProduct.query.filter(SaledProduct.debt_s>0, SaledProduct.date.between(d, s)).all()
            return jsonify(saled_product_schema.dump(alyukabond))
        elif request.method == 'POST':
            id = request.args.get('id')
            data = request.get_json()
            obj = SaledProduct.query.get(id)
            if obj.debt_s >= data.get('amount_s'):
                obj.total_price_s = obj.total_price_s
                obj.total_price_d = obj.total_price_d
                obj.payed_price_d += data.get('amount_d')
                obj.payed_price_s += data.get('amount_s')
                obj.debt_d -= data.get('amount_d')
                obj.debt_s -= data.get('amount_s')
                payed = PayedDebt(amount_d=data.get('amount_d'), agreement_num=obj.agreement_num, amount_s=data.get('amount_s'), user=data.get('user'), saled_id = obj.id)
                db.session.add(payed)
                db.session.commit()
                balance_add(data.get('amount_d'))
                return jsonify(msg="Success")
            return jsonify(msg="You are entered more then debt")
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


#payed debt filter
@bp.route('/payed-debt')
def payed_debt():
    from_d = request.args.get('from')
    to_d = request.args.get('to')
    agr_num = request.args.get('agreement_number')
    provider = request.args.get('provider')
    query = f"SELECT * FROM payed_debt WHERE"  
    query += f" payed_debt.user like '%{provider}%' AND" if provider is not None else ''
    query += f" agreement_number='{agr_num}' AND" if agr_num is not None else ''
    query += f" date BETWEEN '{from_d}' AND '{to_d}' AND" if from_d and to_d else ''
    query = query[:-4]
    prds = db.session.execute(text(query)).fetchall()
    return jsonify(payed_debt_schema.dump(prds))


# balans
@bp.route('/balance')
@jwt_required()
def balance():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from', f"{date.today():%Y-%m-%d}").split('-')
        to_d = request.args.get('to', f"{date.today():%Y-%m-%d}").split('-')
        name = request.args.get('name')
        d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
        s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        if name == "balance":
            w_t = WriteTransaction.query.all()
            balance_d = Balance.query.filter_by(valuta='d').first()
            data = {
                'balance_d':balance_d.amount,
                "transactions":transaction_schemas.dump(w_t)
            }
            return jsonify(data)
        elif name == 'profit':
            saled = SaledProduct.query.with_entities(func.sum(SaledProduct.payed_price_d)).filter(SaledProduct.date.between(d, s)).all()
            aluminy = AluminyNakladnoy.query.with_entities(func.sum(AluminyNakladnoy.total_price_d)).filter(AluminyNakladnoy.date.between(d, s)).all()
            glue = Glue.query.with_entities(func.sum(Glue.total_price_d)).filter(Glue.date.between(d, s)).all()
            sticker = StickerNakladnoy.query.with_entities(func.sum(StickerNakladnoy.total_price_d)).filter(StickerNakladnoy.date.between(d, s)).all()
            exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.date.between(d, s)).all()
            saled_sum = saled[0][0] if saled[0][0] else 0
            aluminy_sum = aluminy[0][0] if aluminy[0][0] else 0
            glue_sum = glue[0][0] if glue[0][0] else 0 
            sticker_sum = sticker[0][0] if sticker[0][0] else 0 
            expence = exp[0][0] if exp[0][0] else 0
            data = saled_sum - (aluminy_sum + glue_sum + sticker_sum + expence)
            return jsonify({"profit":[data]})
        elif name == 'expence':
            exp = Expence.query.all()
            return jsonify(expence_schema.dump(exp))
        elif name == 'total':
            saled = SaledProduct.query.filter(SaledProduct.date.between(d, s)).all()
            return jsonify(saled_product_schema.dump(saled))
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


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
                        amount_s=data.get('amount_s'),
                        amount_d=data.get('amount_d'),
                        user = data.get('user'),
                        description = data.get('description'),
                        status = data.get('status')
                        )
                db.session.add(write)
                db.session.commit()
                balance_add(data.get("amount_d"))
            else:
                write = WriteTransaction(
                        amount_s=data.get('amount_s'),
                        amount_d=data.get('amount_d'),
                        user = data.get('user'),
                        description = data.get('description'),
                        status = data.get('status')
                        )
                db.session.add(write)
                db.session.commit()
                balance_minus(data.get("amount_d"))
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
@jwt_required()
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
                f'L{count}': f"{product.product.color1.name}, {product.product.color2.name if product.product.color2 else ''}",
                f'M{count}': f"{product.product.list_length}, {product.product.list_width}",
                f'N{count}': "list",
                f'P{count}': product.product.quantity
            }
            for cell_address, value in data_to_write.items():
                destination_sheet[cell_address] = value
            destination_wb.save(destination_excel_file)
        destination_wb.close()
        return send_from_directory("../report", "report.xlsx")
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401

