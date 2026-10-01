from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from extensions import db, limiter
from models import User
bp=Blueprint('auth',__name__)

@bp.route('/register', methods=['GET','POST'])
@limiter.limit('10 per minute')
def register():
    if current_user.is_authenticated: return redirect(url_for('player.home'))
    if request.method=='POST':
        u=request.form.get('username','').strip(); e=request.form.get('email','').strip().lower(); p=request.form.get('password',''); c=request.form.get('confirm','')
        if not u or not e or not p: flash('All fields are required.','error')
        elif p!=c: flash('Passwords do not match.','error')
        elif len(p)<8: flash('Password must be at least 8 characters.','error')
        elif User.query.filter(or_(User.minecraft_username.ilike(u), User.email.ilike(e))).first(): flash('Username or email already exists.','error')
        else:
            user=User(minecraft_username=u,email=e,password_hash=generate_password_hash(p)); db.session.add(user); db.session.commit(); login_user(user,remember=True); return redirect(url_for('player.home'))
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET','POST'])
@limiter.limit('10 per minute')
def login():
    if request.method=='POST':
        ident=request.form.get('identifier','').strip(); p=request.form.get('password','')
        user=User.query.filter(or_(User.minecraft_username.ilike(ident),User.email.ilike(ident))).first()
        if user and user.account_status=='ACTIVE' and check_password_hash(user.password_hash,p): login_user(user,remember=True); return redirect(url_for('player.home'))
        flash('Invalid credentials or inactive account.','error')
    return render_template('auth/login.html')

@bp.post('/logout')
def logout(): logout_user(); return redirect(url_for('player.home'))
