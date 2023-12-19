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

    @validates('username')
    def validate_username(self, key, username):
        if not username or username =='':
            raise AssertionError('Username required')
        user = Users.query.filter_by(username=username).first()
        if user:
            raise AssertionError('This username already exists')
        return username
        
    @validates('role')
    def validate_role(self, key, role):
        if not role:
            raise AssertionError('Role required')
        if role not in ['a', 'se', 'e']:
            raise AssertionError('Role shoude be (a/se/e)')
        return role
        

class ExchangeRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())

    @validates('rate')
    def validate_rate(self, key, rate):
        if not rate:
            raise AssertionError('Rate required')
        return rate


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
    status = db.Column(db.String) 

    @validates("type_material")
    def validate_type_material(self, key, type_material):
        if not type_material:
            raise AssertionError("Type material required")
        return type_material
        
    @validates("weight")
    def validate_weight(self, key, weight):
        if not weight:
            raise AssertionError("Type material required")
        return weight

    total, payed =0, 0
    @validates("total_price")
    def validate_total_pricet_s(self, key, total_price_s):
        global total
        if not total_price_s:
            raise AssertionError("Total price required")
        total = total_price_s
        return total_price_s

    @validates("payed_price")
    def validate_payed_price_s(self, key, payed_price_s):
        global payed
        if not payed_price_s:
            raise AssertionError("Payed price required")
        payed = payed_price_s
        return payed_price_s
    
    @validates("debt")
    def validate_debt_s(self, key, debt_s):
        if debt_s != total - payed:
            raise AssertionError("Sum of debt and payed price are not equal to total sum")
        return debt_s


class MaterialAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index1 = db.Column(db.Boolean, default=True)
    amount = db.Column(db.Float)

#
class GranulaAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sklad = db.Column(db.Boolean, default=False)
    weight = db.Column(db.Float)


class GranulaPoteriya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_weight = db.Column(db.Float)
    granula_weight = db.Column(db.Float)
    provider = db.Column(db.String)
    poteriya = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.now())

    @validates('material_weight')
    def validate_material_weight(self, key, material_weight):
        if not material_weight:
            raise AssertionError("Material weigth required")
        return material_weight

    @validates('granula_weight')
    def validate_granula_weight(self, key, granula_weight):
        if not granula_weight:
            raise AssertionError("Granula weigth required")
        return granula_weight


class Setka(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setka_type = db.Column(db.Integer)
    bulk = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())


class Color(db.Model):
    __tablename__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    aluminy = db.relationship('Aluminy', back_populates='color')
    aluminyamount = db.relationship('AluminyAmount', back_populates='color')


class AluminyNakladnoy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partiya = db.Column(db.Integer)
    total_weight = db.Column(db.Float)  
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    provider = db.Column(db.String)
    aluminy = db.relationship('Aluminy', back_populates='nakladnoy')
    date = db.Column(db.DateTime, default=datetime.now())
    payed_debt = db.relationship('PayedDebt',  backref=db.backref('aluminy_nakladnoy', passive_deletes=True), cascade='all, delete-orphan', lazy=True)

    total, payed = 0, 0
    @validates("total_price_s")
    def validate_total_pricet_s(self, key, total_price_s):
        global total
        if not total_price_s:
            raise AssertionError("Total price required")
        total = total_price_s
        return total_price_s

    @validates("payed_price_s")
    def validate_payed_price_s(self, key, payed_price_s):
        global payed
        if not payed_price_s:
            raise AssertionError("Payed price required")
        payed = payed_price_s
        return payed_price_s
    
    @validates("debt_s")
    def validate_debt_s(self, key, debt_s):
        global total, payed
        if debt_s != total - payed:
            raise AssertionError("Sum of debt and payed price are not equal to total sum")
        return debt_s


class Aluminy(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    color_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color = db.relationship('Color', back_populates='aluminy', lazy=True)
    nakladnoy = db.relationship('AluminyNakladnoy', back_populates='aluminy', lazy=True)
    nakladnoy_id = db.Column(db.Integer, db.ForeignKey("aluminy_nakladnoy.id"))
    thickness = db.Column(db.Float, nullable=False)
    list_width = db.Column(db.Float, default=1.22)
    list_length = db.Column(db.Float, default=0)
    roll_weight = db.Column(db.Float, default=0)
    price_per_kg = db.Column(db.Float)
    price = db.Column(db.Float)
    partiya = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, nullable=False)

    @validates("price_per_kg")
    def validate_price_per_kg(self, key, price):
        if not price:
            raise AssertionError("Price required")
        return price
        
    @validates("color_id")
    def validate_type_aluminy(self, key, color):
        if not color:
            raise AssertionError("Color required")
        return color
        
    @validates("thickness")
    def validate_thickness(self, key, thickness):
        if not thickness:
            raise AssertionError("Thickness required")
        return thickness


class AluminyAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color = db.relationship('Color',   back_populates='aluminyamount', lazy=True)
    thickness = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, default=1.22)  # m
    surface = db.Column(db.Float)
    weight = db.Column(db.Float)


class Glue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thickness = db.Column(db.Float)
    weight = db.Column(db.Float, default=0)   # gramm
    width = db.Column(db.Float, default=1.22)
    quantity = db.Column(db.Integer)
    length = db.Column(db.Float, default=0)
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
    payed_debt = db.relationship('PayedDebt',  backref=db.backref('glue', passive_deletes=True), cascade='all, delete-orphan', lazy=True)

    @validates("thickness")
    def validate_thickness(self, key, thickness):
        if not thickness:
            raise AssertionError("Thickness required")
        return thickness

    total, payed =0, 0
    @validates("total_price_s")
    def validate_total_pricet_s(self, key, total_price_s):
        global total
        if not total_price_s:
            raise AssertionError("Total price required")
        total = total_price_s
        return total_price_s

    @validates("payed_price_s")
    def validate_payed_price_s(self, key, payed_price_s):
        global payed
        if not payed_price_s:
            raise AssertionError("Payed price required")
        payed = payed_price_s
        return payed_price_s
    
    @validates("debt_s")
    def validate_debt_s(self, key, debt_s):
        global total, payed
        if debt_s != total - payed:
            raise AssertionError("Sum of debt and payed price are not equal to total sum")
        return debt_s


class GlueAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surface = db.Column(db.Float)
    thickness = db.Column(db.Float)
    weight = db.Column(db.Float)  # gramm
    width = db.Column(db.Float, default=1.22)
    index1 = db.Column(db.Boolean, default=True)


class StickerNakladnoy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partiya = db.Column(db.Integer)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    provider = db.Column(db.String)
    sticker = db.relationship('Sticker', back_populates='nakladnoy')
    date = db.Column(db.DateTime, default=datetime.now())
    payed_debt = db.relationship('PayedDebt',  backref=db.backref('sticker_nakladnoy', passive_deletes=True), cascade='all, delete-orphan', lazy=True)

    total, payed = 0, 0
    @validates("total_price_s")
    def validate_total_pricet_s(self, key, total_price_s):
        global total
        if not total_price_s:
            raise AssertionError("Total price required")
        total = total_price_s
        return total_price_s

    @validates("payed_price_s")
    def validate_payed_price_s(self, key, payed_price_s):
        global payed
        if not payed_price_s:
            raise AssertionError("Payed price required")
        payed = payed_price_s
        return payed_price_s
    
    @validates("debt_s")
    def validate_debt_s(self, key, debt_s):
        global total, payed
        if debt_s != total - payed:
            raise AssertionError("Sum of debt and payed price are not equal to total sum")
        return debt_s


class Sticker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_sticker = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Float, default=1.22)
    quantity = db.Column(db.Integer)
    length = db.Column(db.Float)
    surface = db.Column(db.Float)
    price_per_surface = db.Column(db.Float)
    price = db.Column(db.Float)
    partiya = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    nakladnoy = db.relationship('StickerNakladnoy', back_populates='sticker', lazy=True)
    nakladnoy_id = db.Column(db.Integer, db.ForeignKey("sticker_nakladnoy.id"))

    @validates("type_sticker")
    def validate_type_sticker(self, key, type_sticker):
        if not type_sticker:
            raise AssertionError("Type sticker required")
        if type_sticker not in [100, 150, 450]:
            raise AssertionError('Type sticker type shoude be (100/150/450)')
        return type_sticker
    
    @validates("price_per_surface")
    def validate_total_pricet_s(self, key, price):
        if not price:
            raise AssertionError("Price required")
    

class StickerAmount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_sticker = db.Column(db.Integer)
    width = db.Column(db.Float, default=1.22)
    surface = db.Column(db.Float)


class Alyukabond(db.Model):
    __tablename__ = 'alyukabond'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.String)
    type_product = db.Column(db.Integer, nullable=False)
    sort = db.Column(db.Integer)
    color1_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color2_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color1 = db.relationship('Color', foreign_keys=[color1_id])
    color2 = db.relationship('Color', foreign_keys=[color2_id])
    list_length = db.Column(db.Float)
    list_width = db.Column(db.Float, default=1.22)
    al_thickness = db.Column(db.Float, nullable=False)
    product_thickness = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    provider = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())

    @validates("type_product")
    def validate_type_product(self, key, type_product):
        if not type_product:
            raise AssertionError("Type product required")
        if type_product not in [100, 150, 450]:
            raise AssertionError('Type product shoude be (100/150/450)')
        return type_product

    @validates("color1")
    def validate_color1(self, key, color1):
        if not color1:
            raise AssertionError("Color1 required")
        return color1

    @validates("al_thickness")
    def validate_al_thickness(self, key, al_thickness):
        if not al_thickness:
            raise AssertionError("Aluminy thickness required")
        return al_thickness

    @validates("product_thickness")
    def validate_product_thickness(self, key, product_thickness):
        if not product_thickness:
            raise AssertionError("Product thickness required")
        return product_thickness


class PayedDebt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    user = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now())
    saled_id = db.Column(db.Integer, db.ForeignKey("saled_product.id", ondelete='CASCADE'))
    aluminy_nakladnoy_id = db.Column(db.Integer, db.ForeignKey("aluminy_nakladnoy.id", ondelete='CASCADE'))
    glue_id = db.Column(db.Integer, db.ForeignKey("glue.id", ondelete='CASCADE'))
    sticker_nakladnoy_id = db.Column(db.Integer, db.ForeignKey("sticker_nakladnoy.id", ondelete='CASCADE'))


class AlyukabondAmount(db.Model):
    __tablename__ = 'alyukabond_amount'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    size = db.Column(db.String)
    type_product = db.Column(db.Integer, nullable=False)
    sort = db.Column(db.String)
    color1_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color2_id = db.Column(db.Integer, db.ForeignKey("color.id"))
    color1 = db.relationship('Color', foreign_keys=[color1_id])
    color2 = db.relationship('Color', foreign_keys=[color2_id])
    list_length = db.Column(db.Float)
    list_width = db.Column(db.Float, default=1.22)
    al_thickness = db.Column(db.Float)
    product_thickness = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    product_id = db.relationship('SelectedProduct', backref='product')
    

class SelectedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saled_id = db.Column(db.Integer, db.ForeignKey("saled_product.id")) 
    quantity = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey("alyukabond_amount.id")) 


class SaledProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver = db.Column(db.String)
    customer = db.Column(db.String)
    vehicle_number = db.Column(db.String)
    agreement_num = db.Column(db.Integer)
    total_price_d = db.Column(db.Float)  
    total_price_s = db.Column(db.Float)  
    payed_price_d = db.Column(db.Float)
    payed_price_s = db.Column(db.Float)
    debt_d = db.Column(db.Float)
    debt_s = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())
    products = db.relationship('SelectedProduct',  backref=db.backref('saledproduct', passive_deletes=True), cascade='all, delete-orphan', lazy=True)
    payed_debt = db.relationship('PayedDebt',  backref=db.backref('saledproduct', passive_deletes=True), cascade='all, delete-orphan', lazy=True)

    @validates("agreement_num")
    def validate_agreement_num(self, key, agreement_num):
        if not agreement_num:
            raise AssertionError("Agreement number required")
        return agreement_num
    
    total, payed =0, 0
    @validates("total_price_s")
    def validate_total_pricet_s(self, key, total_price_s):
        global total
        if not total_price_s:
            raise AssertionError("Total price required")
        total = total_price_s
        return total_price_s

    @validates("payed_price_s")
    def validate_payed_price_s(self, key, payed_price_s):
        global payed
        if not payed_price_s:
            raise AssertionError("Payed price required")
        payed = payed_price_s
        return payed_price_s
    
    @validates("debt_s")
    def validate_debt_s(self, key, debt_s):
        global total, payed
        if debt_s != total - payed:
            raise AssertionError("Sum of debt and payed price are not equal to total sum")
        return debt_s


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)

    
class ExpenceIntent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)


class ExpenceUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)


class Expence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    user = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())

    @validates('user')
    def validate_user(self, key, user):
        if not user:
            raise AssertionError('User required')
        return user
    

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    valuta = db.Column(db.String)
    index1 = db.Column(db.Boolean, default=True)


class WriteTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String)
    status = db.Column(db.String)
    description = db.Column(db.String)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime, default=datetime.now())

    @validates('user')
    def validate_user(self, key, user):
        if not user:
            raise AssertionError('User required')
        return user

    @validates('status')
    def validate_status(self, key, status):
        if not status:
            raise AssertionError('Status required')
        return status


class BlacklistToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)


class Makaron(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color1 = db.Column(db.String)
    color2 = db.Column(db.String)
    al_thickness = db.Column(db.Float)
    list_length = db.Column(db.Float)
    weight = db.Column(db.Float)
