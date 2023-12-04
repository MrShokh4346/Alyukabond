from main.models import *

def add_aluminy_amount(thickness=None, width=None, color=None, type=None, length=0, roll_weight=0, quantity=1):
    amount = AluminyAmount.query.filter_by(thickness=thickness, color=color, type_aluminy=type).first()
    if not amount:
        amount = AluminyAmount(color=color, thickness=thickness, width=width, type_aluminy=type, surface=0, weight=0)
        db.session.add(amount)
        db.session.commit()
    surface = length * quantity * width
    amount.surface += surface
    amount.weight += roll_weight * quantity
    db.session.commit()
    return surface


def update_aluminy_amount(material:Aluminy=None, thickness=None, color=None, type=None, list_length=None, list_width=1.22, roll_weight=0, quantity=1, extra_length=None, extra_weight=None):
    extra_length = list_length - material.list_length if list_length!=material.list_length else list_length
    extra_weight = roll_weight - material.roll_weight
    extra_quantity = quantity - material.quantity if quantity!=material.quantity else quantity
    amount = AluminyAmount.query.filter_by(thickness=material.thickness, color=material.color, type_aluminy=material.type_aluminy).first()
    amount1 = AluminyAmount.query.filter_by(thickness=thickness, color=color, type_aluminy=type).first()
    if amount1 is None:
        amount1 = AluminyAmount(color=color, thickness=thickness, type_aluminy=type, surface=0, weight=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        surface = extra_length * extra_quantity  * list_width
        weight = extra_weight * extra_quantity * (-1) if extra_weight<0 and extra_quantity<0 else extra_weight * extra_quantity
        if extra_length != list_length and extra_quantity != quantity:
            surface = material.list_length * extra_quantity * list_width
            surface += extra_length * quantity * list_width
        amount.surface += surface 
        amount.weight += weight 
    else:
        amount.surface -= material.list_length * material.quantity * list_width
        amount.weight -= material.roll_weight * material.quantity
        surface = list_length * list_width * quantity
        amount1.surface += surface
        amount1.weight += roll_weight * quantity
        db.session.commit()
    return surface


def add_glue_amount(width=1.22, length=0, roll_weight=0, quantity=1):
    amount = GlueAmount.query.filter_by(index1=True).first()
    if not amount:
        amount = GlueAmount(surface = 0, weight = 0)
        db.session.add(amount)
        db.session.commit()
    surface = length * quantity * width
    amount.surface += surface
    amount.weight += roll_weight * quantity
    db.session.commit()
    return surface


def update_glue_amount(material:Glue=None, length=None, width=1.22, roll_weight=0, quantity=0):
    extra_length = length - material.length if length!=material.length else length
    extra_weight = roll_weight - material.weight
    extra_quantity = quantity - material.quantity if quantity!=material.quantity else quantity
    amount = GlueAmount.query.filter_by(index1=True).first()
    if amount is None:
        amount = GlueAmount(surface = 0, weight = 0)
        db.session.add(amount)
        db.session.commit()
    surface = extra_length * extra_quantity  * width
    if extra_length != length and extra_quantity != quantity:
        surface = material.length * extra_quantity * width
        surface += extra_length * quantity * width
    amount.surface += surface 
    amount.weight += extra_weight * quantity 
    db.session.commit()
    return surface


def add_sticker_amount(width=1.22,  type=None, length=0, quantity=1):
    amount = StickerAmount.query.filter_by(type_sticker=type).first()
    if not amount:
        amount = StickerAmount(width=width, type_sticker=type, surface=0)
        db.session.add(amount)
        db.session.commit()
    surface = width * length * quantity
    amount.surface += surface
    db.session.commit()
    return surface


def update_sticker_amount(material:Sticker=None,type=None, length=None, width=1.22,  quantity=0):
    extra_length = length - material.length if length!=material.length else length
    extra_quantity = quantity - material.quantity if quantity!=material.quantity else quantity
    amount = StickerAmount.query.filter_by(type_sticker=material.type_sticker).first()
    amount1 = StickerAmount.query.filter_by( type_sticker=type).first()
    if amount1 is None:
        amount1 = StickerAmount(type_sticker=type, surface=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        surface = extra_length * extra_quantity  * width
        if extra_length != length and extra_quantity != quantity:
            surface = material.length * extra_quantity * width
            surface += extra_length * quantity * width
        amount.surface += surface 
    else:
        amount.surface -= material.length * material.quantity * width
        surface = length * quantity * width
        amount1.surface += surface
        db.session.commit()
    return surface


def add_alyukabond_amount(type=None, sort=None, color1=None, color2=None, length=None, al_thickness=None, product_thickness=None, quantity=1):
    amount = AlyukabondAmount.query.filter_by( type_product = type, sort = sort, color1 = color1, color2 = color2,
            list_length = length, al_thickness = al_thickness, product_thickness = product_thickness).first()
    if not amount:
        amount = AlyukabondAmount(type_product = type, sort = sort, color1 = color1, color2 = color2, list_length = length,
                        al_thickness = al_thickness, product_thickness = product_thickness, quantity=0)
        db.session.add(amount)
        db.session.commit()
    amount.quantity += quantity
    db.session.commit()


def update_alyukabond_aluminy(amount1, amount2):
    aluminy1 = AluminyAmount.query.filter_by(thickness=amount1.al_thickness, color=amount1.color1, type_aluminy=amount1.type_product).first()
    aluminy2 = AluminyAmount.query.filter_by(thickness=amount1.al_thickness, color=amount1.color2, type_aluminy=amount1.type_product).first()
    aluminy3 = AluminyAmount.query.filter_by(thickness=amount2.al_thickness, color=amount2.color1, type_aluminy=amount2.type_product).first()
    aluminy4 = AluminyAmount.query.filter_by(thickness=amount2.al_thickness, color=amount2.color2, type_aluminy=amount2.type_product).first()
    old_surface = amount1.list_length * amount1.list_width * amount1.quantity
    old_weight = 1.4 * amount1.quantity
    aluminy1.surface += old_surface
    aluminy1.weight += old_weight
    aluminy2.surface += old_surface
    aluminy2.weight += old_weight
    new_surface = amount2.list_length * amount2.list_width * amount2.quantity
    new_weight = 1.4 * amount2.quantity
    print(aluminy3)
    if (aluminy3 is not None and aluminy4 is not None) and (aluminy3.surface > new_surface and aluminy4.surface > new_surface):
        aluminy3.surface -= new_surface
        aluminy3.weight -= new_weight
        aluminy4.surface -= new_surface
        aluminy4.weight -= new_weight
        db.session.commit()
    else:
        print(1)
        raise AssertionError(f"There isn't enaugh this type of aluminy in warehouse")


def update_alyukabond_sticker(amount1, amount2):
    sticker1 = StickerAmount.query.filter_by(type_sticker=amount1.type_product).first()
    sticker2 = StickerAmount.query.filter_by(type_sticker=amount2.type_product).first()
    old_surface = amount1.list_length * amount1.list_width * amount1.quantity
    sticker1.surface += old_surface
    new_surface = amount2.list_length * amount2.list_width * amount2.quantity
    if sticker2 is not None and sticker2.surface > new_surface:
        sticker2.surface -= new_surface
        db.session.commit()
    else:
        AssertionError(f"There isn't enaugh {sticker2.type_sticker}  sticker in warehouse")


def update_alyukabond_glue(amount1, amount2):
    surface1 = amount1.list_length * amount1.list_width * amount1.quantity
    surface2 = amount2.list_length * amount2.list_width * amount2.quantity
    extra = surface1 - surface2
    glue = GlueAmount.query.filter_by(index1=True).first()
    glue.surface += extra
    db.session.commit()


def update_alyukabond_amount(material:Alyukabond=None, type=None, sort=None, color1=None, color2=None, length=None, width=1.22, al_thickness=None, product_thickness=None, quantity=1):
    amount = AlyukabondAmount.query.filter_by(type_product=material.type_product, color1=material.color1, color2=material.color2,
            list_length=material.list_length, al_thickness=material.al_thickness, product_thickness=material.product_thickness).first()
    amount1 = AlyukabondAmount.query.filter_by( type_product = type, color1 = color1, color2 = color2,
            list_length = length, al_thickness = al_thickness, product_thickness = product_thickness).first()
    if (amount is not None and amount1 is not None) and amount == amount1:
        amount.quantity += quantity
        db.session.commit()
    else:
        if amount1 is not None:
            update_alyukabond_aluminy(amount1=amount, amount2=amount1)
            update_alyukabond_sticker(amount1=amount, amount2=amount1)
            update_alyukabond_glue(amount1=amount, amount2=amount1)
            amount.quantity -= material.quantity
            amount1.quantity += quantity
            db.session.commit()
        else:
            amount1 = AlyukabondAmount(
                type_product = type,
                sort = sort,
                color1 = color1,
                color2 = color2,
                list_length = length,
                list_width = width,
                al_thickness = al_thickness,
                product_thickness = product_thickness,
                quantity = quantity
            )
            update_alyukabond_aluminy(amount1=amount, amount2=amount1)
            update_alyukabond_sticker(amount1=amount, amount2=amount1)
            update_alyukabond_glue(amount1=amount, amount2=amount1)
            db.session.add(amount1)
            amount.quantity -= material.quantity
            db.session.commit()


def check(turi=None, rangi1=None, rangi2=None, qalinligi=None, yuza=None, ogirlik=None, sort=1, miqdor=1):
    for obj in ['alyuminy', 'sticker', 'glue', 'granula']:
        amount = {
            'alyuminy': AluminyAmount.query.filter_by(color=rangi1, type_aluminy=turi, thickness=qalinligi).first(),
            'sticker': StickerAmount.query.filter_by(type_sticker=turi).first(),
            'glue': GlueAmount.query.filter_by(index1=True).first(),
            'granula':GranulaAmount.query.filter_by(sklad=False).first()
        }.get(obj, False)

        aluminy2 = AluminyAmount.query.filter_by(color=rangi2, type_aluminy=turi, thickness=qalinligi).first() if obj == 'alyuminy' else None
        if aluminy2 is not None and aluminy2.surface > yuza * miqdor:
            aluminy2.surface -= yuza * miqdor
            amount.weight -= ogirlik[obj] * miqdor
        elif aluminy2 is None and obj == 'alyuminy':
            raise AssertionError(f"There isn't enaugh {rangi2} aluminy in warehouse")

        if amount is not None:
            if amount.surface and (amount.surface > yuza * miqdor) if obj!="granula" else False:
                amount.surface -= yuza * miqdor 
            if amount.weight and (amount.weight > ogirlik[obj] * miqdor) if obj!="sticker" else False:
                amount.weight -= ogirlik[obj] * miqdor
            msg="success"
            
        else:
            raise AssertionError(f"There isn't enaugh {rangi1 if obj=='alyuminy' else ''} {obj} in warehouse")

            break
    db.session.commit()
    return msg