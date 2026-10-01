from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, abort
from werkzeug.security import check_password_hash
from sqlalchemy import func, or_
from extensions import db, socketio, limiter
from models import Admin, User, Order, RevenuePeriod, AdminAuditLog
from services.admin import audit
bp=Blueprint('admin',__name__,url_prefix='/admin')

def admin_user():
    aid=session.get('admin_id'); return db.session.get(Admin,aid) if aid else None
def required(fn):
    from functools import wraps
    @wraps(fn)
    def w(*a,**k):
        if not admin_user(): return redirect(url_for('admin.login'))
        return fn(*a,**k)
    return w
@bp.route('/login',methods=['GET','POST'])
@limiter.limit('8 per minute')
def login():
    if request.method=='POST':
        a=Admin.query.filter_by(username=request.form.get('username','')).first()
        if a and check_password_hash(a.password_hash,request.form.get('password','')): session['admin_id']=a.id; return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.','error')
    return render_template('admin/login.html')
@bp.post('/logout')
def logout(): session.pop('admin_id',None); return redirect(url_for('admin.login'))
def stats():
    period=RevenuePeriod.query.filter_by(ended_at=None).order_by(RevenuePeriod.started_at.desc()).first(); start=period.started_at if period else datetime(1970,1,1,tzinfo=timezone.utc)
    q=Order.query
    return {'players':User.query.count(),'orders':q.count(),'pending':q.filter_by(status='PENDING').count(),'approved':q.filter_by(status='APPROVED').count(),'rejected':q.filter_by(status='REJECTED').count(),'lifetime':db.session.query(func.coalesce(func.sum(Order.amount),0)).filter(Order.status=='APPROVED').scalar(),'period':db.session.query(func.coalesce(func.sum(Order.amount),0)).filter(Order.status=='APPROVED',Order.verified_at>=start).scalar()}
@bp.get('/')
@required
def dashboard(): return render_template('admin/dashboard.html',stats=stats(),orders=Order.query.order_by(Order.created_at.desc()).limit(100).all())
@bp.get('/orders')
@required
def orders():
    q=Order.query; status=request.args.get('status'); cat=request.args.get('category'); s=request.args.get('q','').strip()
    if status in {'PENDING','APPROVED','REJECTED'}: q=q.filter_by(status=status)
    if cat in {'RANK','ITEM','IGM'}: q=q.filter_by(category=cat)
    if s: q=q.join(User).filter(or_(User.minecraft_username.ilike(f'%{s}%'),User.email.ilike(f'%{s}%'),Order.verification_code.ilike(f'%{s}%')))
    return render_template('admin/orders.html',orders=q.order_by(Order.created_at.desc()).all())
@bp.get('/orders/<int:oid>')
@required
def order_detail(oid): return render_template('admin/order_detail.html',order=Order.query.get_or_404(oid))
def change(oid,status):
    o=Order.query.get_or_404(oid); a=admin_user()
    if o.status!='PENDING': flash('Order already finalized.','error'); return redirect(url_for('admin.order_detail',oid=oid))
    o.status=status; o.verified_at=datetime.now(timezone.utc); o.verified_by=a.id; db.session.commit(); audit(a.id,'ORDER_'+status,'ORDER',o.id,o.verification_code); socketio.emit('order_update',{'id':o.id,'status':o.status}); return redirect(request.referrer or url_for('admin.dashboard'))
@bp.post('/orders/<int:oid>/approve')
@required
def approve(oid): return change(oid,'APPROVED')
@bp.post('/orders/<int:oid>/reject')
@required
def reject(oid): return change(oid,'REJECTED')
@bp.get('/players')
@required
def players():
    s=request.args.get('q','').strip(); q=User.query
    if s:q=q.filter(or_(User.minecraft_username.ilike(f'%{s}%'),User.email.ilike(f'%{s}%')))
    return render_template('admin/players.html',players=q.order_by(User.created_at.desc()).all())
@bp.get('/players/<int:uid>')
@required
def player_detail(uid): return render_template('admin/player_detail.html',player=User.query.get_or_404(uid))
@bp.post('/players/<int:uid>/reset')
@required
def reset_player(uid):
    if request.form.get('confirm')!='RESET': abort(400)
    u=User.query.get_or_404(uid); count=u.orders.count(); u.orders.delete(synchronize_session=False); db.session.commit(); audit(admin_user().id,'PLAYER_DATA_RESET','USER',uid,f'{count} orders cleared'); return redirect(url_for('admin.player_detail',uid=uid))
@bp.post('/revenue/reset')
@required
def reset_revenue():
    if request.form.get('confirm')!='RESET': abort(400)
    now=datetime.now(timezone.utc); p=RevenuePeriod.query.filter_by(ended_at=None).first()
    if p:p.ended_at=now
    db.session.add(RevenuePeriod(started_at=now,created_by=admin_user().id)); db.session.commit(); audit(admin_user().id,'REVENUE_RESET','REVENUE_PERIOD',None,'Started new revenue period'); return redirect(url_for('admin.dashboard'))
@bp.get('/audit')
@required
def audit_log(): return render_template('admin/audit.html',logs=AdminAuditLog.query.order_by(AdminAuditLog.created_at.desc()).limit(500).all())
