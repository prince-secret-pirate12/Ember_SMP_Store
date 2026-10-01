import secrets, string
from models import Order
from extensions import db

def unique_code():
    alphabet=string.ascii_uppercase+string.digits
    while True:
        code='EMBER-'+''.join(secrets.choice(alphabet) for _ in range(6))
        if not Order.query.filter_by(verification_code=code).first(): return code

def create_order(user, product_id, product):
    order=Order(verification_code=unique_code(), user_id=user.id, category=product['category'], product_id=product_id, product_name=product['name'], amount=product['price'])
    db.session.add(order); db.session.commit(); return order
