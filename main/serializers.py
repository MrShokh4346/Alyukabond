from marshmallow import Schema, validates, fields, post_load
from main.models import *
import re


class UsersSerializer(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True)
    username = fields.String(required=True)
    role = fields.String(required=True)

user_schema = UsersSerializer()
users_schema = UsersSerializer(many=True)


class ColorSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()

color_schema = ColorSerializer()
colors_schema = ColorSerializer(many=True)


# class AluminyThicknessSerializer(Schema):
#     id = fields.Integer(dump_only=True)
#     thickness = fields.Float()

# aluminy_thickness_schema = AluminyThicknessSerializer()
# aluminy_thickness_schemas = AluminyThicknessSerializer(many=True)


# class AlyukabondLengthSerializer(Schema):
#     id = fields.Integer(dump_only=True)
#     length = fields.Float()

# alyukabond_length_schema = AlyukabondLengthSerializer()
# alyukabond_length_schemas = AlyukabondLengthSerializer(many=True)


class PayedDebtSerializer(Schema):
    id = fields.Integer(dump_only=True)
    amount_s = fields.Float(required=True)
    amount_d = fields.Float(required=True)
    agr_num = fields.String()
    user = fields.String()
    date = fields.DateTime(format='%Y-%m-%d %X')

payed_debt_schema = PayedDebtSerializer(many=True)


class GranulaMaterialSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    type_material = fields.String(required=True)
    total_weight = fields.Float(required=True)
    waste = fields.Integer(required=True)
    weight = fields.Float(required=True)
    price_per_kg = fields.Float(required=True)
    price_per_kg_s = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    payed_debt = fields.Nested(PayedDebtSerializer, many=True, dump_only=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

material_schemas = GranulaMaterialSerializer(many=True)
material_schema = GranulaMaterialSerializer()

salafan_schema = GranulaMaterialSerializer(many=True)


class MaterialAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    amount = fields.Float()

material_amount_schema = MaterialAmountSerializer()


class SetkaSerializer(Schema):
    id = fields.Integer(dump_only=True)
    setka_type = fields.String(required=True)
    bulk = fields.Float(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

setka_schemas = SetkaSerializer(many=True)
setka_schema = SetkaSerializer()


class AluminySerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    color = fields.Nested(ColorSerializer, dump_only=True, required=True)
    thickness = fields.Float(required=True)
    list_width = fields.Float(required=True)
    list_length = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    roll_weight = fields.Float(required=True)
    partiya = fields.Integer(required=True)
    price_per_kg = fields.Float(required=True)
    price = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

aluminy_schemas = AluminySerializer(many=True)
aluminy_schema = AluminySerializer()


class AluminyNakladnoySerializer(Schema):
    id = fields.Integer(dump_only=True)
    partiya = fields.Integer(required=True)
    total_weight = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    payed_debt = fields.Nested(PayedDebtSerializer, many=True, dump_only=True)
    sticker = fields.Nested(AluminySerializer, many=True, dump_only=True)

aluminy_nakladnoy_schema = AluminyNakladnoySerializer(many=True)
aluminy_nakladnoy_schem = AluminyNakladnoySerializer()



class AluminyAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    color = fields.Nested(ColorSerializer, dump_only=True, required=True)
    type_aluminy = fields.Integer(required=True)
    thickness = fields.Float(required=True)
    width = fields.Float(required=True)
    surface = fields.Float(required=True)
    weight = fields.Float(required=True)

al_amount_schema = AluminyAmountSerializer(many=True)
al_amount_schem = AluminyAmountSerializer()


class GlueSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_glue = fields.String(required=True)
    thickness = fields.Float(required=True)
    surface = fields.Float(required=True)
    weight = fields.Float(required=True)
    width = fields.Float(required=True)
    length = fields.Float(required=True)
    price_per_kg = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    total_price_d = fields.Float(required=True, format=":.2f")
    total_price_s = fields.Decimal(required=True, places=2)
    payed_price_d = fields.Float(required=True, format=":.2f")
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    payed_debt = fields.Nested(PayedDebtSerializer,  dump_only=True, required=True, many=True)


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
    partiya = fields.Integer(required=True)
    length = fields.Float(required=True)    
    surface = fields.Float(required=True)
    price = fields.Float(required=True)
    price_per_surface = fields.Float(required=True)
    total_surface = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    quantity = fields.Integer(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    payed_debt = fields.Nested(PayedDebtSerializer,  dump_only=True, required=True, many=True)


sticker_schemas = StickerSerializer(many=True)
sticker_schema = StickerSerializer()


class StickerAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_sticker = fields.Integer(required=True)
    width = fields.Float(required=True)
    surface = fields.Float(required=True)

sticker_amount_schemas = StickerAmountSerializer(many=True)


class StickerNakladnoySerializer(Schema):
    id = fields.Integer(dump_only=True)
    partiya = fields.Integer(required=True)
    total_weight = fields.Float(required=True)
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    provider = fields.String(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    payed_debt = fields.Nested(PayedDebtSerializer, many=True, dump_only=True)
    sticker = fields.Nested(StickerSerializer, many=True, dump_only=True)

sticker_nakladnoy_schema = StickerNakladnoySerializer(many=True)


class ExpenceSerializer(Schema):
    id = fields.Integer(dump_only=True)
    status = fields.String()
    description = fields.String(required=True)
    seb = fields.String(required=True)
    user = fields.String(required=True)
    price = fields.Decimal(required=True, places=2)
    price_s = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

expence_schema = ExpenceSerializer(many=True)


class GranulaPoteriyaSerializer(Schema):
    id = fields.Integer(dump_only=True)
    granula_weight = fields.String(required=True)
    material_weight = fields.String(required=True)
    provider = fields.String(required=True)
    poteriya = fields.Float(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

gr_sklad_schema = GranulaPoteriyaSerializer(many=True)
gr_sklad_schem = GranulaPoteriyaSerializer()


class GranulaSAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    weight = fields.String(required=True)
    data = fields.String(required=True)

gr_amount_schema = GranulaSAmountSerializer()


class AlyukabondAmountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    type_product = fields.Integer(required=True)
    type_sticker = fields.Integer(required=True)
    sort = fields.String(required=True)
    color1 = fields.Nested(ColorSerializer, dump_only=True, required=True)
    color2 = fields.Nested(ColorSerializer, dump_only=True, required=True)
    list_length = fields.Float(required=True)
    list_width = fields.Float(required=True)
    al_thickness = fields.Float(required=True)
    product_thickness = fields.Float(required=True)
    quantity = fields.Integer(required=True)

alyukabond_amount_schema = AlyukabondAmountSerializer(many=True)
alyukabond_amount_schem = AlyukabondAmountSerializer()



class AlyukabondSerializer(Schema):
    id = fields.Integer(dump_only=True)
    type_product = fields.Integer(required=True)
    type_sticker = fields.Integer(required=True)
    sort = fields.String(required=True)
    color1 = fields.Nested(ColorSerializer, dump_only=True, required=True)
    color2 = fields.Nested(ColorSerializer, dump_only=True, required=True)
    list_length = fields.Float(required=True)
    list_width = fields.Float(required=True)
    al_thickness = fields.Float(required=True)
    product_thickness = fields.Float(required=True)
    provider = fields.String(required=True)
    quantity = fields.Integer(required=True)
    editable = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')


alyukabond_schemas = AlyukabondSerializer(many=True)
alyukabond_schema = AlyukabondSerializer()


class SelectedProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    quantity = fields.Integer(required=True)
    alyukabond = fields.Nested(AlyukabondAmountSerializer, dump_only=True, required=True)

selected_product_schema = SelectedProductSerializer(many=True)  


class SaledProductSerializer(Schema):
    id = fields.Integer(dump_only=True)
    provider = fields.String(required=True)
    customer = fields.String(required=True)
    saler = fields.String(required=True)
    vehicle_number = fields.String(required=True)
    quantity = fields.Integer()
    agreement_num = fields.Integer()
    total_price_d = fields.Float(required=True)
    total_price_s = fields.Float(required=True)
    payed_price_d = fields.Float(required=True)
    payed_price_s = fields.Float(required=True)
    debt_d = fields.Float(required=True)
    debt_s = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')
    editable = fields.Boolean(required=True)
    # products = fields.Nested(SelectedProductSerializer, dump_only=True, required=True, many=True)
    payed_debt = fields.Nested(PayedDebtSerializer,  dump_only=True, required=True, many=True)

saled_product_schema = SaledProductSerializer(many=True)
saled_product_schem = SaledProductSerializer()



class WriteTransactionSerializer(Schema):
    id = fields.Integer(dump_only=True)
    user = fields.String(required=True)
    status = fields.String(required=True)
    amount_s = fields.Integer(required=True)
    amount_d = fields.Integer(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

transaction_schemas = WriteTransactionSerializer(many=True)
transaction_schema = WriteTransactionSerializer()

class MakaronSerializer(Schema):
    id = fields.Integer(dump_only=True)
    color1 = fields.String(required=True)
    color2 = fields.String(required=True)
    al_thickness = fields.Float(required=True)
    list_length = fields.Float(required=True)
    weight = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

makaron_schema = MakaronSerializer(many=True)


class GranulaOtxodSerializer(Schema):
    id = fields.Integer(dump_only=True)
    weight = fields.Float(required=True)
    date = fields.DateTime(required=True, format='%Y-%m-%d')

granula_otxod_schema = GranulaOtxodSerializer(many=True)


class ExchangeRateSerializer(Schema):
    id = fields.Integer(dump_only=True)
    rate = fields.Float()
    date = fields.DateTime(required=True, format='%Y-%m-%d %X')

exchange_rate_schema = ExchangeRateSerializer()


class AddBalanceUserSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = rate = fields.String()

add_balance_users_schema = AddBalanceUserSerializer(many=True)