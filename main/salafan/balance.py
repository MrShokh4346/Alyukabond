from main.models import *

def balance_minus(amount):
    balance_d = Balance.query.filter_by(valuta='d').first()
    if not balance_d:
        balance_d = Balance(amount=0, valuta='d')
        db.session.add(balance_d)
        db.session.commit()
    if balance_d.amount < amount:
        raise AssertionError("На балансе недостаточно денег")
    balance_d.amount -= amount
    db.session.commit()
