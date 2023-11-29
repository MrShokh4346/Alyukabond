from main.models import *

def add_aluminy_amount(id=None, thickness=None, width=None, color=None, type=None, length=0, roll_weight=0, quantity=1):
    if id is not None:
        amount = AluminyAmount.query.get(id)
    else:
        obj = AluminyAmount.query.filter_by(thickness=thickness, color=color, type_aluminy=type).first()
        if obj:
            raise AssertionError("This size aleady exists")
        else:
            amount = AluminyAmount(color=color, thickness=thickness, width=width, type_aluminy=type, surface=0, weight=0)
            db.session.add(amount)
            db.session.commit()
    amount.surface += length * quantity * width
    amount.weight += roll_weight * quantity
    db.session.commit()
    return amount.surface


def update_aluminy_amount(material:Aluminy=None, thickness=None, color=None, type=None, list_length=None, list_width=None, roll_weight=0, quantity=None):
    extra_length = list_length - material.list_length
    extra_weight = roll_weight - material.roll_weight
    amount = AluminyAmount.query.filter_by(thickness=material.thickness, color=material.color, type_aluminy=material.type_aluminy).first()
    amount1 = AluminyAmount.query.filter_by(thickness=thickness, color=color, type_aluminy=type).first()
    if amount1 is None:
        amount1 = AluminyAmount(color=color, thickness=thickness, type_aluminy=type, surface=0, weight=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        amount1.surface += extra_length * (quantity if quantity else material.quantity) * (list_width if list_width else material.list_width)
        amount1.weight += extra_weight * (quantity if quantity else material.quantity)
    else:
        amount.surface -= list_length * (quantity if quantity else material.quantity) * (list_width if list_width else material.list_width)
        amount.weight -= list_length * (quantity if quantity else material.quantity)
        amount1.surface += abs(list_length) * (quantity if quantity else material.quantity) * (list_width if list_width else material.list_width)
        amount1.weight += abs(list_length) * (quantity if quantity else material.quantity)
        db.session.commit()
    return amount1.surface



def add_glue_amount(width=2.44, length=0, roll_weight=0, quantity=1):
    amount = GlueAmount.query.filter_by(index1=True).first()
    if not amount:
        amount = GlueAmount(surface = 0, weight = 0)
        db.session.add(amount)
        db.session.commit()
    amount.surface += length * quantity * width
    amount.weight += roll_weight * quantity
    db.session.commit()
    return amount.surface


def update_glue_amount(material:Glue=None,length=None, width=2.44, roll_weight=0, quantity=None):
    extra_length = length - material.length
    extra_weight = roll_weight - material.weight
    amount = GlueAmount.query.filter_by(index1=True).first()
    if amount is None:
        amount = GlueAmount(surface = 0, weight = 0)
        db.session.add(amount)
        db.session.commit()
    amount.surface += extra_length * (quantity if quantity else material.quantity) * (width if width else material.width)
    amount.weight += extra_weight * (quantity if quantity else material.quantity)
    db.session.commit()
    return amount.surface


def add_sticker_amount(id=None, width=2.44,  type=None, length=0, quantity=1):
    amount = StickerAmount.query.get(id)
    if not amount:
        obj = StickerAmount.query.filter_by(type_sticker=type).first()
        if obj:
            raise AssertionError("This size aleady exists")
        else:
            amount = StickerAmount(width=width, type_sticker=type, surface=0)
            db.session.add(amount)
            db.session.commit()
    amount.surface += width * length * quantity
    db.session.commit()
    return amount.surface


def update_sticker_amount(material:Sticker=None,type=None, length=None, width=2.44,  quantity=1):
    extra_length = length - material.length
    amount = StickerAmount.query.filter_by(type_sticker=material.type_sticker).first()
    amount1 = StickerAmount.query.filter_by( type_sticker=type).first()
    if amount1 is None:
        amount1 = StickerAmount(type_sticker=type, surface=0)
        db.session.add(amount1)
        db.session.commit()
    if amount == amount1:
        amount1.surface += extra_length * (quantity if quantity else material.quantity) * (width if width else material.width)
    else:
        amount.surface -= length * (quantity if quantity else material.quantity) * (width if width else material.width)
        amount1.surface += abs(length) * (quantity if quantity else material.quantity) * (width if width else material.width)
        db.session.commit()
    return amount1.surface