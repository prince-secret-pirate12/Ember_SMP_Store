from flask import Blueprint, render_template, current_app, abort, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from extensions import db, socketio
from models import Order
from services.catalog import PRODUCTS
from services.orders import create_order
bp=Blueprint('player',__name__)

def cfg(): return dict(smp_name=current_app.config['SMP_NAME'],server_ip=current_app.config['SERVER_IP'],discord=current_app.config['DISCORD_URL'],logo=current_app.config['SMP_LOGO'],qr=current_app.config['PAYMENT_QR'])
@bp.app_context_processor
def inject_brand(): return cfg()
@bp.get('/')
def home(): return render_template('player/home.html')
@bp.get('/ranks')
def ranks(): return render_template('player/products.html',title='Ranks',products=[(k,v) for k,v in PRODUCTS.items() if v['category']=='RANK'])
@bp.get('/store')
def store(): return render_template('player/products.html',title='Minecraft In-Game Items',products=[(k,v) for k,v in PRODUCTS.items() if v['category']=='ITEM'])
@bp.get('/igm')
def igm(): return render_template('player/products.html',title='In-Game Money',products=[(k,v) for k,v in PRODUCTS.items() if v['category']=='IGM'])
@bp.get('/checkout/<product_id>')
@login_required
def checkout(product_id):
    p=PRODUCTS.get(product_id)
    if not p: abort(404)
    import secrets
    token=secrets.token_urlsafe(24); session['checkout_token']=token
    return render_template('player/checkout.html',product=p,product_id=product_id,submission_token=token)
@bp.post('/orders/create')
@login_required
def submit_order():
    product_id=request.form.get('product_id'); p=PRODUCTS.get(product_id)
    if not p: abort(400)
    token=request.form.get('submission_token','')
    if not token or token != session.pop('checkout_token', None): abort(409)
    order=create_order(current_user,product_id,p); session['last_order_code']=order.verification_code
    socketio.emit('order_update',{'id':order.id,'status':order.status}); return redirect(url_for('player.order_success',code=order.verification_code))
@bp.get('/orders/success/<code>')
@login_required
def order_success(code):
    o=Order.query.filter_by(verification_code=code,user_id=current_user.id).first_or_404(); return render_template('player/order_success.html',order=o)
@bp.get('/my-orders')
@login_required
def my_orders(): return render_template('player/orders.html',orders=Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all())
@bp.get('/profile')
@login_required
def profile():
    orders=Order.query.filter_by(user_id=current_user.id).all(); approved=[o for o in orders if o.status=='APPROVED']; spent=sum((o.amount for o in approved),0)
    return render_template('player/profile.html',orders=orders,spent=spent)
