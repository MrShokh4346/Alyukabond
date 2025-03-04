from main.models import *
from sqlalchemy import text
from main.serializers import *


def add_material_amount(material_weight):
    material_amount = MaterialAmount.query.filter_by(index1=True).first()
    if not material_amount:
        material_amount = MaterialAmount(amount=0, index1=True)
        db.session.add(material_amount)
        db.session.commit()
    material_amount.amount += material_weight
    db.session.commit()


def add_granula_amount(granula_weight):
    amount = GranulaAmount.query.filter_by(sklad=False).first()
    if not amount:
        amount = GranulaAmount(weight=0)
        db.session.add(amount)
    amount.weight += granula_weight
    db.session.commit()


def add_aluminy_amount(thickness=None, width=None, color_id=None, length=0, roll_weight=0, quantity=1):
    amount = AluminyAmount.query.filter_by(thickness=thickness, color_id=color_id).first()
    if not amount:
        amount = AluminyAmount(color_id=color_id, thickness=thickness, width=width, surface=0, weight=0)
        db.session.add(amount)
    surface = length * quantity * width
    amount.surface += surface
    amount.weight += roll_weight * quantity
    db.session.commit()


def update_aluminy_amount(material:Aluminy=None, thickness=None, color=None, list_length=None, list_width=1.22, roll_weight=0, quantity=1, extra_length=None, extra_weight=None):
    extra_length = list_length - material.list_length 
    extra_weight = roll_weight - material.roll_weight
    extra_quantity = quantity - material.quantity 
    amount = AluminyAmount.query.filter_by(thickness=material.thickness, color_id=material.color_id).first()
    amount1 = AluminyAmount.query.filter_by(thickness=thickness, color_id=color).first()
    if amount1 is None:
        amount1 = AluminyAmount(color_id=color, thickness=thickness, surface=0, weight=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        surface = material.list_length * extra_quantity * list_width
        weight = material.roll_weight * extra_quantity 
        surface += extra_length * quantity * list_width
        weight += extra_weight * quantity
        amount.surface += surface 
        amount.weight += weight 
    else:
        amount.surface -= material.list_length * material.quantity * list_width
        amount.weight -= material.roll_weight * material.quantity
        surface = list_length * list_width * quantity
        amount1.surface += surface
        amount1.weight += roll_weight * quantity
        db.session.commit()


def add_glue_amount(thickness=None, width=1.22, length=0, roll_weight=0, quantity=1):
    amount = GlueAmount.query.filter_by(index1=True).first()
    if not amount:
        amount = GlueAmount(surface = 0, thickness=thickness, weight = 0)
        db.session.add(amount)
    surface = length * quantity * width
    amount.surface += surface
    amount.weight += roll_weight * 1000
    db.session.commit()


def update_glue_amount(material:Glue=None, thickness=None, length=None, width=1.22, roll_weight=0, quantity=0):
    extra_length = length - material.length 
    extra_weight = (roll_weight - material.weight) * 1000
    extra_quantity = quantity - material.quantity 
    amount = GlueAmount.query.filter_by(index1=True).first()
    if amount is not None:
        surface = material.length * extra_quantity * width
        weight = material.weight 
        surface += extra_length * quantity * width
        weight += extra_weight
        amount.surface += surface 
        amount.weight += weight 



def add_sticker_amount(width=1.22,  type=None, length=0, quantity=1):
    amount = StickerAmount.query.filter_by(type_sticker=type).first()
    if not amount:
        amount = StickerAmount(width=width, type_sticker=type, surface=0)
        db.session.add(amount)
    surface = width * length * quantity
    amount.surface += surface
    db.session.commit()
    return surface


def update_sticker_amount(material:Sticker=None,type=None, length=None, width=1.22,  quantity=0):
    extra_length = length - material.length 
    extra_quantity = quantity - material.quantity 
    amount = StickerAmount.query.filter_by(type_sticker=material.type_sticker).first()
    amount1 = StickerAmount.query.filter_by( type_sticker=type).first()
    if amount1 is None:
        amount1 = StickerAmount(type_sticker=type, surface=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        surface = material.length * extra_quantity * width
        surface += extra_length * quantity * width
        amount.surface += surface 
    else:
        amount.surface -= material.length * material.quantity * material.width
        surface = length * quantity * width
        amount1.surface += surface
        db.session.commit()
    return surface


def add_alyukabond_amount(type=None, type_product=None, sort=None, color1=None, color2=None, length=None, al_thickness=None, product_thickness=None, quantity=1):
    amount = AlyukabondAmount.query.filter_by(type_sticker = type, sort = sort, color1_id = color1, color2_id = color2,
            list_length = length, al_thickness = al_thickness, product_thickness = product_thickness, type_product=type_product).first()
    if not amount:
        amount = AlyukabondAmount(type_sticker = type, sort = sort, color1_id = color1, color2_id = color2, list_length = length,
                        al_thickness = al_thickness, product_thickness = product_thickness, type_product=type_product,  quantity=0)
        db.session.add(amount)
        db.session.commit()
    amount.quantity += quantity
    db.session.commit()


def check(turi=None, rangi1=None, rangi2=None, qalinligi=None, length=None, width=None, miqdor=1):
    ogirlik = {
        'алюмина':1.4 * length/2.44,
        'клея':270,
        'гранула':10.3 * length/2.44,
        "наклейка":0
    }
    for obj in ['алюмина', 'наклейка', 'клея', 'гранула']:
        amount = {
            'алюмина': AluminyAmount.query.filter_by(color_id=rangi1, thickness=qalinligi).first(),
            'наклейка': StickerAmount.query.filter_by(type_sticker=turi).first(),
            'клея': GlueAmount.query.filter_by(index1=True).first(),
            'гранула':GranulaAmount.query.filter_by(sklad=False).first()
        }.get(obj, False)
        yuza = {
            'алюмина':length * (width + 0.02),
            "наклейка":length * (width + 0.02),
            "клея":length * (width + 0.06)
        }.get(obj, False)
        aluminy2 = AluminyAmount.query.filter_by(color_id=rangi2, thickness=qalinligi).first() if obj == 'алюмина' else None
        if amount is not None and aluminy2 is not None and aluminy2.surface > yuza * miqdor:
            aluminy2.surface -= yuza * miqdor
            aluminy2.weight -=  ogirlik[obj] * miqdor
        elif aluminy2 is None and obj == 'алюмина':
            raise AssertionError(f"На складе недостаточно {obj} данного типа")

        if amount is not None:
            if obj!='гранула':
                if amount.surface and (amount.surface > yuza * miqdor):
                    amount.surface -= yuza * miqdor 
                else:
                    raise AssertionError(f"На складе недостаточно {obj} данного типа")
            if obj!='наклейка':
                if amount.weight and (amount.weight >  ogirlik[obj] * miqdor):
                    amount.weight -=  ogirlik[obj] * miqdor
                else:
                    raise AssertionError(f"На складе недостаточно {obj} данного типа")
            msg="success"
            
        else:
            raise AssertionError(f"На складе недостаточно {obj} данного типа")

            break
    db.session.commit()
    return msg


def filter_amount(name=None, type=None, sort=None, thickness=None, color1=None, color2=None, from_d=None, to_d=None, length=None):
    t = "type_product" if name.count('alyukabond')==1 else f"type_sticker"
    c = "color1_id" if name.count('alyukabond')==1 else "color_id"
    thkn = "al_thickness" if name.count('alyukabond')==1 else "thickness"
    query = f"SELECT * FROM {name} WHERE"   # aluminy_amount, glue_amount, sticker_amount, alyukabond_amount
    query += f" {t}='{type}' AND" if type is not None else ''
    # query += f" editable='f' AND" if len(name.split('_'))==1 else ''
    query += f" sort='{sort}' AND" if sort is not None else ''
    query += f" {c}='{color1}' AND" if color1 is not None else ''
    query += f" color2_id='{color2}' AND" if color2 is not None else ''
    query += f" list_length='{length}' AND" if length is not None else ''
    query += f" {thkn}='{thickness}' AND" if thickness is not None else ''
    query += f" quantity>0 AND" if name=='alyukabond_amount' else ''
    if (from_d and to_d) and len(name.split('_')) == 1:
        query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
    query = query[:-4]
    query += " ORDER BY date DESC" if len(name.split("_"))==1 else '' 
    prds = db.session.execute(text(query)).fetchall()
    if name in ['alyukabond', 'aluminy', "aluminy_amount", "alyukabond_amount"]:
        data = []
        count = 0
        for prd in prds:
            if name == 'aluminy':
                data.append(aluminy_schema.dump(prd))
                c = Color.query.filter_by(id=prd.color_id).first()
                data[count]["color"] = color_schema.dump(c)
            elif name == "aluminy_amount":
                data.append(al_amount_schem.dump(prd))
                c = Color.query.filter_by(id=prd.color_id).first()
                data[count]["color"] = color_schema.dump(c)
            elif name == "alyukabond":
                data.append(alyukabond_schema.dump(prd))
                c1 = Color.query.filter_by(id=prd.color1_id).first()
                c2 = Color.query.filter_by(id=prd.color2_id).first()
                data[count]["color1"] = color_schema.dump(c1)
                data[count]["color2"] = color_schema.dump(c2)
            elif name == "alyukabond_amount":
                data.append(alyukabond_amount_schem.dump(prd))
                c1 = Color.query.filter_by(id=prd.color1_id).first()
                c2 = Color.query.filter_by(id=prd.color2_id).first()
                data[count]["color1"] = color_schema.dump(c1)
                data[count]["color2"] = color_schema.dump(c2)
            count += 1
    else:
        data = {
            'glue_amount':glue_amount_schemas.dump(prds) if name == 'glue_amount' else '',
            'sticker_amount':sticker_amount_schemas.dump(prds) if name == 'sticker_amount' else '',
            'sticker':sticker_schemas.dump(prds) if name == 'sticker' else '',
            'glue':glue_schemas.dump(prds) if name == 'glue' else ''
        }.get(name, None)
        if name=="glue_amount":
            for i in range(len(data)):
                data[i]["weight"] = round(data[i]["weight"] / 1000, 3) 
    return data 


def filter_nakladnoy(name=None, partiya=None, provider=None, from_d=None, to_d=None):
    query = f"SELECT * FROM {name} WHERE "   
    query += f"partiya={partiya} AND" if partiya is not None else ''
    query += f" provider like'%{provider}%' AND" if provider is not None else ''
    if (from_d and to_d):
        query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
    query = query[:-4]
    query += " ORDER BY date DESC" 
    prds = db.session.execute(text(query)).fetchall()
    data = []
    count = 0
    for prd in prds:
        data.append(aluminy_nakladnoy_schem.dump(prd))
        p_d = PayedDebt.query.filter_by(aluminy_nakladnoy_id=prd.id).all() if name=='aluminy_nakladnoy' else PayedDebt.query.filter_by(sticker_nakladnoy_id=prd.id).all()
        data[count]["payed_debt"] = payed_debt_schema.dump(p_d)
        count += 1
    return data 


def filter_saled(agr_num=None, customer=None, saler=None, from_d=None, to_d=None):
    query = f"SELECT * FROM saled_product WHERE"  
    query += f" customer like '%{customer}%' AND" if customer is not None else ''
    query += f" saler like '%{saler}%' AND" if saler is not None else ''
    query += f" agreement_num='{agr_num}' AND"if agr_num is not None else ''
    # query += f" editable='0' AND"#if agr_num is not None else ''
    if (from_d and to_d):
        query += f" date BETWEEN '{from_d}' AND '{to_d}' AND"
    query = query[:-4]
    query += " ORDER BY date DESC" 
    prds = db.session.execute(text(query)).fetchall()
    data = []
    count = 0
    for prd in prds:
        data.append(saled_product_schem.dump(prd))
        p_d = PayedDebt.query.filter_by(saled_id=prd.id).all() 
        data[count]["payed_debt"] = payed_debt_schema.dump(p_d)
        count += 1
    return data 
