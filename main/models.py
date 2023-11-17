from main import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates 
import re 
from datetime import datetime
from sqlalchemy.orm import backref


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    role = db.Column(db.String(2), default='e') #a - admin, se - super employee, e - employee

    @property
    def password(self):
        raise AttributeError("Passwprd was unrreadable")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())


class GranulaMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    type_material = db.Column(db.String)  #rossiya, paket, atxod
    total_weight = db.Column(db.Float)
    waste = db.Column(db.Integer)
    weight = db.Column(db.Float)   
    price_per_kg = db.Column(db.Float)
    total_price = db.Column(db.Float)  
    payed_price = db.Column(db.Float)
    debt = db.Column(db.Float)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String)  # Sklad, sexga
    log = db.relationship('LogMaterial', backref='granula_material')


class MaterialAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index1 = db.Column(db.Boolean, default=True)
    amount = db.Column(db.Float)


class GranulaAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sklad = db.Column(db.Boolean)
    amount = db.Column(db.Float)


class GranulaSklad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_weight = db.Column(db.Float)
    granula_weight = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())


class Setka(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setka_type = db.Column(db.Integer)
    bulk = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())


class Aluminy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String)
    thickness = db.Column(db.Float)
    list_width = db.Column(db.Float)
    list_length = db.Column(db.Float)
    roll_weight = db.Column(db.Float)
    price_per_kg = db.Column(db.Float)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
    log = db.relationship('LogMaterial', backref=backref('aluminy'))


class AluminyAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String)
    thickness = db.Column(db.Float)
    width = db.Column(db.Float)
    length = db.Column(db.Float)
    weight = db.Column(db.Float)


class Glue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thickness = db.Column(db.Float)
    weight = db.Column(db.Float)
    surface = db.Column(db.Float)
    price_per_kg = db.Column(db.Float)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
    log = db.relationship('LogMaterial', backref=backref('glue'))


class GlueAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surface = db.Column(db.Float)
    thickness = db.Column(db.Float)
    weight = db.Column(db.Float)
    width = db.Column(db.Float)
    index1 = db.Column(db.Boolean)


class Sticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_sticker = db.Column(db.Integer)
    width = db.Column(db.Float)
    weight = db.Column(db.Float)
    surface = db.Column(db.Float)
    price_per_surface = db.Column(db.Float)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
    log = db.relationship('LogMaterial', backref=backref('sticker'))


class StickerAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_sticker = db.Column(db.String)
    width = db.Column(db.Float)
    surface = db.Column(db.Float)
    thickness = db.Column(db.Float)


class Alyukabond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.String)
    type_product = db.Column(db.String)
    sort = db.Column(db.String)
    color = db.Column(db.String)
    list_length = db.Column(db.Float)
    list_width = db.Column(db.Float)
    al_thickness = db.Column(db.Float)
    product_thickness = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())


class AlyukabondAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.String)
    type_product = db.Column(db.String)
    sort = db.Column(db.String)
    color = db.Column(db.String)
    list_length = db.Column(db.Float)
    list_width = db.Column(db.Float)
    al_thickness = db.Column(db.Float)
    product_thickness = db.Column(db.Float)
    quantity = db.Column(db.Integer)


seleceted_products = db.Table('seleceted_products',
    db.Column('alyukabondamount_id', db.Integer, db.ForeignKey('alyukabond_amount.id'), primary_key=True),
    db.Column('saledproduct_id', db.Integer, db.ForeignKey('saled_product.id'), primary_key=True)
)


class SaledProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String)
    customer = db.Column(db.String)
    agreement_num = db.Column(db.Integer)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())
    products = db.relationship('AlyukabondAmount', secondary=seleceted_products, lazy='subquery', backref=db.backref('saledproduct', lazy=True))



class LogMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    granula_id = db.Column(db.Integer, db.ForeignKey("granula_material.id")) 
    aluminy_id = db.Column(db.Integer, db.ForeignKey("aluminy.id")) 
    glue_id = db.Column(db.Integer, db.ForeignKey("glue.id")) 
    sticker_id = db.Column(db.Integer, db.ForeignKey("sticker.id")) 
    miqdor = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())


class Expence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())