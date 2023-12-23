from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from werkzeug.security import generate_password_hash

    
db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG_FILE')
   
    
    from .views import main_views, analysis_views
    app.register_blueprint(main_views.bp)
  
    app.register_blueprint(analysis_views.bp)

    from .cache import cache
    cache.init_app(app)



    return app

    # ORM
    # db.init_app(app)
    # migrate.init_app(app, db)
    # cache.init_app(app)

    # from . import models

    
    # 필터 
    # from .filter import format_datetime
    # app.jinja_env.filters['datetime'] = format_datetime


