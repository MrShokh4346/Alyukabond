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
    exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.status=='salafan', Expence.seb=="учитывает", Expence.date.between(frm, to)).all()
    rasxod = exp[0][0] if exp[0][0] else 0
    salafan = granula[0][1] if granula[0][1] else 0 
    granula = granula[0][0] if granula[0][0] else 1 
    avg_narx = material[0][0] if material[0][0] else 0 
    salafan_narx = salafan*avg_narx if salafan else 0
    grn_narx = (salafan_narx + rasxod )/ granula
    data = {
        "grn_kg_narx":grn_narx,
        "grn_rasxod":rasxod
    }
    return data


# granula sebistoimost
@bp.route('/granula-seb')
def granula_seb():
    from_d = request.args.get('from').split('-')
    to_d = request.args.get('to').split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    data = salafan_rasxod(d, s)
    return jsonify([{"granula_seb":data['grn_kg_narx']}])


# sebestoymost
@bp.route('/price')
def alyukabond_price():
    f_date = request.args.get('from')
    t_date = request.args.get('to')
    type_product = request.args.get('type_product')
    from_d = f_date.split('-')
    to_d = t_date.split('-')
    d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
    s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
    thkn = float(request.args.get('al_thickness', 0))
    typ = int(request.args.get('type_sticker', 0))
    color1 = request.args.get('color1')
    color2 = request.args.get('color2')
    color2 = 1 if type_product=='1' else color2

    grnl = salafan_rasxod(frm=d, to=s)

    # bir oyda chiqgan alyukabond
    query = f"select sum(surface) from alyukabond where date between '{f_date}' and '{t_date}'"

    alyukabond_all_surface = db.session.execute(text(query)).fetchall()
    alyukabond_all_surface = alyukabond_all_surface[0][0] if alyukabond_all_surface[0][0] else 1

    # berilga tur buyicha
    query1 = f"select sum(surface) from alyukabond where  al_thickness='{thkn}' and color1_id='{color1}' and color2_id='{color2}' and type_product='{type_product}' and date between '{f_date}' and '{t_date}'"
    alyukabond_surface = db.session.execute(text(query1)).fetchall()
    alyukabond_surface = alyukabond_surface[0][0] if alyukabond_surface[0][0] else 0

    # aluminy narx o'rtacha
    aluminy1 = Aluminy.query.with_entities(func.avg(Aluminy.price_per_kg)).filter(Aluminy.thickness==thkn, Aluminy.color_id==color1, Aluminy.date.between(d, s)).all()
    aluminy1 =  aluminy1[0][0] if aluminy1[0][0] else 0

    aluminy2 = Aluminy.query.with_entities(func.avg(Aluminy.price_per_kg)).filter(Aluminy.thickness==thkn, Aluminy.color_id==color2, Aluminy.date.between(d, s)).all()
    aluminy2 =  aluminy2[0][0] if aluminy2[0][0] else 0

    # kley narx o'rtacha
    glue = Glue.query.with_entities(func.avg(Glue.price_per_kg)).filter(Glue.date.between(d, s)).all()
    glue =  glue[0][0] / 1000 if glue[0][0] else 0

    # nakleyka natx o'rtahca
    sticker = Sticker.query.with_entities(func.avg(Sticker.price_per_surface)).filter(Sticker.type_sticker==typ, Sticker.date.between(d, s)).all()
    sticker = sticker[0][0] if sticker[0][0] else 0

    # rasxodlar
    exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.status!='salafan', Expence.seb=="учитывает", Expence.date.between(d, s)).all()
    # bitta alyukabondga minadigan rasxod
    exp = exp[0][0] if exp[0][0] else 0
    rasxod = (exp / alyukabond_all_surface)

    if type_product == '2':
        al1 = 1.4 / 3 * aluminy1
        al2 = 1.4 / 3 * aluminy2
        st = 3.0256 * 2 / 3 * sticker
        gl = (270 / 3) * glue
        grn = 10.3 / 3 * grnl["grn_kg_narx"]
        seb = (al1 + al2 + st + gl + grn + rasxod) if alyukabond_surface else 0
    else:
        al1 = 1.4 / 3 * aluminy1
        al2 = 1.4 / 3 * aluminy2
        st = 3.0256 / 3 * sticker
        gl = (270 / 3) * glue
        grn = 10.3 / 3 * grnl["grn_kg_narx"]
        seb = (al1 + al2 + st + gl + grn + rasxod) if alyukabond_surface else 0
    data = [{
        "aluminy_color1":round(al1, 2),
        "aluminy_color2":round(al2, 2),
        "glue":round(gl, 2),
        "sticker":round(st, 2),
        "granula":round(grn, 2),
        "rasxod_salafan":round(grnl["grn_rasxod"], 2),
        "rasxod_alyukabond":round(exp, 2),
        "quantity_alyukabond":round(alyukabond_surface, 2),
        "sebistoymost":round(seb, 2)
    }]
    return jsonify(data)


# Qarzlar xisobot
@bp.route('/report/debt', methods=['GET', 'POST'])
@jwt_required()
def report_debt():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        if request.method == 'GET':
            from_d = request.args.get('from')
            to_d = request.args.get('to')
            if from_d=='' :
                from_d = date.today() - timedelta(days=30)
                to_d = date.today() + timedelta(days=1)
            partiya = request.args.get('partiya')                                                                                              
            provider = request.args.get('provider')
            fr = request.args.get('filter', None)
            aluminy = filter_nakladnoy(name="aluminy_nakladnoy", partiya=partiya, provider=provider, from_d=from_d, to_d=to_d) if fr=='aluminy' else None
            glue = glue_schemas.dump(Glue.query.filter(Glue.date > from_d, Glue.date <= to_d).order_by(Glue.date.desc()).all()) if fr=='glue' else None
            sticker = filter_nakladnoy(name="sticker_nakladnoy", partiya=partiya, provider=provider, from_d=from_d, to_d=to_d) if fr=='sticker' else None
            salafan = salafan_schema.dump(GranulaMaterial.query.filter(GranulaMaterial.date > from_d, GranulaMaterial.date <= to_d).order_by(GranulaMaterial.date.desc()).all()) if fr=='salafan' else None
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
            debt = material.debt_d
            if debt >= data.get('amount_d'):
                material.total_price_s = material.total_price_s
                material.total_price_d = material.total_price_d
                material.payed_price_d += data.get('amount_d')
                material.payed_price_s += data.get('amount_s')
                material.debt_d -= data.get('amount_d')
                material.debt_s -= data.get('amount_s')
                # else:
                #     material.total_price = material.total_price
                #     material.payed_price += data.get('amount_s')
                #     material.debt -= data.get('amount_s') 
                payed = {
                    'aluminy':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), aluminy_nakladnoy_id = material.id),
                    'glue':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), glue_id = material.id),
                    'sticker':PayedDebt(amount_d=data.get('amount_d'), amount_s=data.get('amount_s'), user=data.get('user'), sticker_nakladnoy_id = material.id),
                    'salafan':PayedDebt(amount_s=data.get('amount_s'), user=data.get('user'), salafan_id = material.id)
                }.get(name, None)
                try:
                    db.session.add(payed)
                    balance_minus(data.get('amount_d'))
                    db.session.commit()
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
                return jsonify(msg="Success")
            return jsonify(msg="Вы вошли в нечто большее, чем просто долг"),400
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


# Haqlar xisobot
@bp.route('/report/fee', methods=['GET', 'POST'])
@jwt_required()
def report_fee():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        if request.method == 'GET':
            from_d = request.args.get('from')
            to_d = request.args.get('to')
            if from_d=='' :
                from_d = date.today() - timedelta(days=30)
                to_d = date.today() + timedelta(days=1)
            alyukabond = SaledProduct.query.filter( SaledProduct.date > from_d, SaledProduct.date <= to_d).order_by(SaledProduct.date.desc()).all()
            return jsonify(saled_product_schema.dump(alyukabond))
        elif request.method == 'POST':
            id = request.args.get('id')
            data = request.get_json()
            obj = SaledProduct.query.get(id)
            if obj.debt_d >= data.get('amount_d'):
                obj.total_price_s = obj.total_price_s
                obj.total_price_d = obj.total_price_d
                obj.payed_price_d += data.get('amount_d')
                obj.payed_price_s += data.get('amount_s')
                obj.debt_d -= data.get('amount_d')
                obj.debt_s -= data.get('amount_s')
                payed = PayedDebt(amount_d=data.get('amount_d'), agreement_number=obj.agreement_num, amount_s=data.get('amount_s'), user=data.get('user'), saled_id = obj.id)
                db.session.add(payed)
                db.session.commit()
                balance_add(data.get('amount_d'))
                return jsonify(msg="Success")
            return jsonify(msg="Вы вошли в нечто большее, чем просто долг"), 400
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401


#payed debt filter
@bp.route('/payed-debt')
def payed_debt():
    from_d = request.args.get('from')
    to_d = request.args.get('to')
    id = request.args.get('id')
    agr_num = request.args.get('agreement_number')
    provider = request.args.get('provider')
    name = request.args.get('name')
    if name and from_d and to_d:
            query = {
                'aluminy': f"SELECT * FROM payed_debt WHERE  glue_id is NULL AND  sticker_nakladnoy_id is NULL AND  salafan_id is NULL AND  saled_id is NULL ",
                'glue': f"SELECT * FROM payed_debt WHERE aluminy_nakladnoy_id is NULL AND sticker_nakladnoy_id is NULL AND  salafan_id is NULL AND  saled_id is NULL ",
                'sticker': f"SELECT * FROM payed_debt WHERE glue_id is NULL AND  aluminy_nakladnoy_id is NULL AND  salafan_id is NULL AND  saled_id is NULL ",
                'salafan': f"SELECT * FROM payed_debt glue_id is NULL AND  aluminy_nakladnoy_id is NULL AND  sticker_nakladnoy_id is NULL AND  saled_id is NULL ",
                'saled': f"SELECT * FROM payed_debt WHERE salafan_id is NULL AND glue_id is NULL AND  aluminy_nakladnoy_id is NULL AND  sticker_nakladnoy_id is NULL " 
            }.get(name)
            query += f"AND date BETWEEN '{from_d}' AND '{to_d}'"
            query += " ORDER BY date DESC"
            prds = db.session.execute(text(query)).fetchall()
            return jsonify(payed_debt_schema.dump(prds))
    if id and name:
        query = {
            'aluminy': f"SELECT * FROM payed_debt WHERE aluminy_nakladnoy_id='{id}'",
            'glue': f"SELECT * FROM payed_debt WHERE glue_id='{id}'",
            'sticker': f"SELECT * FROM payed_debt WHERE sticker_nakladnoy_id='{id}'",
            'salafan': f"SELECT * FROM payed_debt WHERE salafan_id='{id}'",
            'saled': f"SELECT * FROM payed_debt WHERE saled_id='{id}'"
        }.get(name)
        query += " ORDER BY date DESC"
        prds = db.session.execute(text(query)).fetchall()
        return jsonify(payed_debt_schema.dump(prds))
    query = f"SELECT * FROM payed_debt WHERE"  
    query += f" payed_debt.user like '%{provider}%' AND" if provider is not None else ''
    query += f" agreement_number like '%{agr_num}%' AND" if agr_num is not None else ''
    query += f" date BETWEEN '{from_d}' AND '{to_d}' AND" if from_d and to_d else ''
    query = query[:-4]
    query += " ORDER BY date DESC"
    prds = db.session.execute(text(query)).fetchall()
    return jsonify(payed_debt_schema.dump(prds))


# balans
@bp.route('/balance')
@jwt_required()
def balance():
    user = db.get_or_404(Users, get_jwt_identity())
    if user.role == 'a':
        from_d = request.args.get('from')
        to_d = request.args.get('to')
        name = request.args.get('name')
        if from_d=='' or from_d is None:
            d = date.today() - timedelta(days=30)
            s = date.today() + timedelta(days=1)
        else:
            d = datetime(int(from_d[0]), int(from_d[1]), int(from_d[2]))
            s = datetime(int(to_d[0]), int(to_d[1]), int(to_d[2]))
        if name == "balance":
            balance_d = Balance.query.filter_by(valuta='d').first()
            data = [{
                'balance_d':f"{balance_d.amount:.2f}"
            }]
            return jsonify(data)
        elif name == 'profit':
            saled = SaledProduct.query.with_entities(func.sum(SaledProduct.payed_price_d)).filter(SaledProduct.editable==False, SaledProduct.date.between(d, s)).all()
            aluminy = AluminyNakladnoy.query.with_entities(func.sum(AluminyNakladnoy.total_price_d)).filter(AluminyNakladnoy.editable==False, AluminyNakladnoy.date.between(d, s)).all()
            glue = Glue.query.with_entities(func.sum(Glue.total_price_d)).filter(Glue.editable==False, Glue.date.between(d, s)).all()
            sticker = StickerNakladnoy.query.with_entities(func.sum(StickerNakladnoy.total_price_d)).filter(StickerNakladnoy.editable==False, StickerNakladnoy.date.between(d, s)).all()
            exp = Expence.query.with_entities(func.sum(Expence.price)).filter(Expence.date.between(d, s)).all()
            saled_sum = saled[0][0] if saled[0][0] else 0
            aluminy_sum = aluminy[0][0] if aluminy[0][0] else 0
            glue_sum = glue[0][0] if glue[0][0] else 0 
            sticker_sum = sticker[0][0] if sticker[0][0] else 0 
            expence = exp[0][0] if exp[0][0] else 0
            data = saled_sum - (aluminy_sum + glue_sum + sticker_sum + expence)
            return jsonify([{"profit":f"{data:.2f}"}])
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
            user = request.args.get("user")
            if user=='undefined':
                user = None
            from_d = request.args.get('from')
            to_d = request.args.get('to')
            query = f"SELECT * FROM write_transaction WHERE "   
            query += f" write_transaction.user like '%{user}%' AND" if user is not None else ''
            query += f" status='{status}' AND" if status is not None else ''
            if (from_d and to_d):
                query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
            query = query[:-4]
            query += " ORDER BY date DESC"
            prds = db.session.execute(text(query)).fetchall()
            if id is not None:
                tr = db.get_or_404(WriteTransaction, id)
                return jsonify(transaction_schema.dump(tr))
            return jsonify(transaction_schemas.dump(prds))
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
                try:
                    db.session.add(write)
                    balance_minus(data.get("amount_d"))
                    db.session.commit()
                except AssertionError as err:
                    return jsonify(msg=f"{str(err)}"), 400
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
        # destination_sheet["M1"] = saled.id + 1000
        destination_sheet["C3"] = saled.date
        destination_sheet["T3"] = saled.date

        destination_sheet["D5"] = saled.agreement_num
        destination_sheet["U5"] = saled.agreement_num

        destination_sheet["D9"] = saled.customer
        destination_sheet["U9"] = saled.customer

        destination_sheet["D12"] = saled.driver
        destination_sheet["U12"] = saled.driver

        destination_sheet["L12"] = saled.vehicle_number
        destination_sheet["AC12"] = saled.vehicle_number
        for product in saled.products:
            count +=1
            data_to_write = {
                f'B{count}': product.alyukabond.name if product.alyukabond.name else "Алюкобонд",
                f'S{count}': product.alyukabond.name if product.alyukabond.name else "Алюкобонд",
                
                f'K{count}': f"{product.alyukabond.color1.name}, {product.alyukabond.color2.name if product.alyukabond.color2.id != 1 else ''}",
                f'AB{count}': f"{product.alyukabond.color1.name}, {product.alyukabond.color2.name if product.alyukabond.color2.id != 1 else ''}",
                
                f'L{count}': f"{product.alyukabond.list_length} * {product.alyukabond.list_width}",
                f'AC{count}': f"{product.alyukabond.list_length} * {product.alyukabond.list_width}",
                
                f'M{count}': "лист",
                f'AD{count}': "лист",
                
                f'O{count}': product.quantity,
                f'AF{count}': product.quantity
            }
            for cell_address, value in data_to_write.items():
                destination_sheet[cell_address] = value
            destination_wb.save(destination_excel_file)
        destination_wb.close()
        return send_from_directory("../report", "report.xlsx")
    else:
        return jsonify(msg="У вас нет полномочий на это действие"), 401

