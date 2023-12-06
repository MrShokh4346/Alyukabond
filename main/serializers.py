from marshmallow import Schema, validates, fields, post_load
from main.models import *
import re


class UserSerializer(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True)
    username = fields.String(required=True)
    role = fields.String(required=True)

user_schema = UserSerializer()
users_schema = UserSerializer(many=True)


class GranulaMaterialSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    type_material = fields.String(required=True)
    total_weight = fields.Float(required=True)
    waste = fields.Integer(required=True)
    weight = fields.Float(required=True)
    price_per_kg = fields.Float(required=True)
    total_price = fields.Float(required=True)
    payed_price = fields.Float(required=True)
    debt = fields.Float(required=True)
    provider = fields.String(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

material_schemas = GranulaMaterialSerializer(many=True)
material_schema = GranulaMaterialSerializer()


class SetkaSerializer(Schema):
    id = fields.Integer(dump_only=True)
    setka_type = fields.String(required=True)
    bulk = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

setka_schemas = SetkaSerializer(many=True)


class AluminySerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    color = fields.String(required=True)
    thickness = fields.Float(required=True)
    list_width = fields.Float(required=True)
    list_length = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    roll_weight = fields.Float(required=True)
    type_aluminy = fields.Integer(required=True)
    price_per_kg = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

aluminy_schemas = AluminySerializer(many=True)
aluminy_schema = AluminySerializer()


class AluminyAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    color = fields.String(required=True)
    type_aluminy = fields.Integer(required=True)
    thickness = fields.Float(required=True)
    width = fields.Float(required=True)
    surface = fields.Float(required=True)
    weight = fields.Float(required=True)

al_amount_schema = AluminyAmountSerializer(many=True)


class GlueSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_glue = fields.String(required=True)
    thickness = fields.Float(required=True)
    surface = fields.Float(required=True)
    weight = fields.Float(required=True)
    length = fields.Float(required=True)
    price_per_kg = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

glue_schemas = GlueSerializer(many=True)
glue_schema = GlueSerializer()


class GlueAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    thickness = fields.Float(required=True)
    surface = fields.Float(required=True)
    weight = fields.Float(required=True)

glue_amount_schema = GlueAmountSerializer()
glue_amount_schemas = GlueAmountSerializer(many=True)



class StickerSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_sticker = fields.Integer(required=True)
    width = fields.Float(required=True)
    length = fields.Float(required=True)    
    surface = fields.Float(required=True)
    total_surface = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

sticker_schemas = StickerSerializer(many=True)
sticker_schema = StickerSerializer()


class StickerAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_sticker = fields.Integer(required=True)
    width = fields.Float(required=True)
    surface = fields.Float(required=True)

sticker_amount_schemas = StickerAmountSerializer(many=True)


class ExpenceSerializer(Schema):
    id = fields.Integer(dump_only=True)
    discription = fields.String(required=True)
    user = fields.String(required=True)
    price = fields.Float(required=True)

expence_schema = ExpenceSerializer(many=True)


class GranulaSkladSerializer(Schema):
    id = fields.Integer(dump_only=True)
    granula_weight = fields.String(required=True)
    material_weight = fields.String(required=True)
    provider = fields.String(required=True)
    data = fields.String(required=True)

gr_sklad_schema = GranulaSkladSerializer(many=True)


class GranulaSAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    weight = fields.String(required=True)
    data = fields.String(required=True)

gr_amount_schema = GranulaSAmountSerializer()


class AlyukabondAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    size = fields.String(required=True)
    type_product = fields.String(required=True)
    sort = fields.String(required=True)
    color1 = fields.String(required=True)
    color2 = fields.String(required=True)
    list_length = fields.Float(required=True)
    list_width = fields.Float(required=True)
    al_thickness = fields.Float(required=True)
    product_thickness = fields.Float(required=True)
    quantity = fields.Integer(required=True)

alyukabond_amount_schema = AlyukabondAmountSerializer(many=True)


class AlyukabondSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    size = fields.String(required=True)
    type_product = fields.String(required=True)
    sort = fields.String(required=True)
    color1 = fields.String(required=True)
    color2 = fields.String(required=True)
    list_length = fields.Float(required=True)
    list_width = fields.Float(required=True)
    al_thickness = fields.Float(required=True)
    product_thickness = fields.Float(required=True)
    provider = fields.String(required=True)
    quantity = fields.Integer(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

alyukabond_schemas = AlyukabondSerializer(many=True)
alyukabond_schema = AlyukabondSerializer()


class SelectedProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    quantity = fields.Integer(required=True)
    product = fields.Nested(AlyukabondAmountSerializer, dump_only=True, required=True)
    

class SaledProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    provider = fields.String(required=True)
    customer = fields.String(required=True)
    agreement_num = fields.Integer()
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    products = fields.Nested(SelectedProductSerializer, dump_only=True, required=True, many=True)

saled_product_schema = SaledProductSerializer(many=True)



class WriteTransactionSerializer(Schema):
    id = fields.Integer(dump_only=True)
    user = fields.String(required=True)
    status = fields.String(required=True)
    amount = fields.Integer(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

transaction_schemas = WriteTransactionSerializer(many=True)
transaction_schema = WriteTransactionSerializer()
