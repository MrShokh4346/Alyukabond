from main.models import *

def balance_minus(amount):
    balance_s = Balance.query.filter_by(valuta='s').first()
    balance_d = Balance.query.filter_by(valuta='d').first()
    if not balance_s:
        balance_s = Balance(amount=0, valuta='s')
        balance_d = Balance(amount=0, valuta='d')
        db.session.add(balance_s)
        db.session.add(balance_d)
        db.session.commit()
    if balance_s.amount < amount:
        raise AssertionError("На балансе недостаточно денег")
    balance_s.amount -= amount
    rate = ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
    balance_d.amount -= amount / rate.rate
    db.session.commit()
