from main.models import *

def balance_minus(amount):
    balance = Balance.query.filter_by(index1=True).first()
    if not balance:
        balance = Balance(amount=0)
        db.session.add(balance)
        db.session.commit()
    if balance.amount < amount:
        raise AssertionError("There is not enough money in the balance")
    balance.amount -= amount
    db.session.commit()


def balance_add(amount):
    balance = Balance.query.filter_by(index1=True).first()
    if not balance:
        balance = Balance(amount=0)
        db.session.add(balance)
        db.session.commit()
    balance.amount += amount
    db.session.commit()
