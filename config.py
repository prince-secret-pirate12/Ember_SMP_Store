import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ember_store.db').replace('postgres://','postgresql://',1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('COOKIE_SECURE','0') == '1'
    SMP_NAME = os.getenv('SMP_NAME','Ember SMP')
    SERVER_IP = os.getenv('SERVER_IP','purgee.playwithbao.com:33446')
    DISCORD_URL = os.getenv('DISCORD_URL','https://discord.gg/K3TwyZJ9m')
    SMP_LOGO = os.getenv('SMP_LOGO','images/ember_smp.jpg')
    PAYMENT_QR = os.getenv('PAYMENT_QR','images/payment_qr.png')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME','admin')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH','')
