from flask import Flask
from config import Config
from extensions import db,login_manager,csrf,socketio,migrate,limiter
from models import User, Admin
from werkzeug.security import generate_password_hash
import click
from routes.auth import bp as auth_bp
from routes.player import bp as player_bp
from routes.admin import bp as admin_bp

def create_app(config=Config):
    app=Flask(__name__); app.config.from_object(config)
    db.init_app(app); login_manager.init_app(app); csrf.init_app(app); socketio.init_app(app); migrate.init_app(app,db); limiter.init_app(app)
    login_manager.login_view='auth.login'
    @login_manager.user_loader
    def load(uid): return db.session.get(User,int(uid))
    app.register_blueprint(auth_bp); app.register_blueprint(player_bp); app.register_blueprint(admin_bp)
    @app.cli.command('create-admin')
    def create_admin():
        username=app.config['ADMIN_USERNAME']; ph=app.config['ADMIN_PASSWORD_HASH']
        if not ph: raise click.ClickException('Set ADMIN_PASSWORD_HASH first.')
        if Admin.query.filter_by(username=username).first(): raise click.ClickException('Admin already exists.')
        db.session.add(Admin(username=username,password_hash=ph)); db.session.commit(); click.echo('Admin created.')
    return app
app=create_app()
if __name__=='__main__': socketio.run(app,debug=True)
