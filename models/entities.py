from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy import Numeric, Index
from extensions import db

def now(): return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    minecraft_username=db.Column(db.String(32), unique=True, nullable=False, index=True)
    email=db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash=db.Column(db.String(255), nullable=False)
    created_at=db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    account_status=db.Column(db.String(20), default='ACTIVE', nullable=False)
    orders=db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')

class Admin(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    created_at=db.Column(db.DateTime(timezone=True), default=now)
    @property
    def is_admin(self): return True

class Order(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    verification_code=db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    category=db.Column(db.String(16), nullable=False, index=True)
    product_id=db.Column(db.String(64), nullable=False)
    product_name=db.Column(db.String(160), nullable=False)
    amount=db.Column(Numeric(10,2), nullable=False)
    status=db.Column(db.String(16), default='PENDING', nullable=False, index=True)
    created_at=db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    verified_at=db.Column(db.DateTime(timezone=True))
    verified_by=db.Column(db.Integer, db.ForeignKey('admin.id'))
    admin=db.relationship('Admin', foreign_keys=[verified_by])
    __table_args__=(Index('ix_order_user_status','user_id','status'),)

class AdminAuditLog(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    admin_id=db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    action=db.Column(db.String(80), nullable=False)
    target_type=db.Column(db.String(40), nullable=False)
    target_id=db.Column(db.String(64))
    details=db.Column(db.Text)
    created_at=db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    admin=db.relationship('Admin')

class RevenuePeriod(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    started_at=db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    ended_at=db.Column(db.DateTime(timezone=True))
    created_by=db.Column(db.Integer, db.ForeignKey('admin.id'))
