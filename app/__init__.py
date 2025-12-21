from flask import Flask
from app.models import db
import os

class PrefixMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        prefix = environ.get('HTTP_X_FORWARDED_PREFIX', '')
        if not prefix:
            prefix = os.environ.get('SCRIPT_NAME', '')
            
        if prefix:
            environ['SCRIPT_NAME'] = prefix
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith(prefix):
                environ['PATH_INFO'] = path_info[len(prefix):]
        return self.app(environ, start_response)

def create_app():
    app = Flask(__name__)
    
    # 强制使用环境变量中的数据库连接字符串
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("未设置 DATABASE_URL 环境变量，请在 .env 文件中配置 MySQL 连接。")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv("SECRET_KEY", "feynman_secret_key")

    app.wsgi_app = PrefixMiddleware(app.wsgi_app)

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.chat import chat_bp
    from app.routes.pet import pet_bp
    from app.routes.shop import shop_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(pet_bp)
    app.register_blueprint(shop_bp)

    with app.app_context():
        db.create_all()
        # 初始化商城皮肤
        from app.models import Skin
        if not Skin.query.first():
            skins = [
                Skin(name="经典款", price=0, description="费曼最喜欢的原始装扮"),
                Skin(name="小博士", price=100, description="戴上眼镜，看起来更聪明了"),
                Skin(name="宇航员", price=500, description="向着星辰大海出发！")
            ]
            db.session.add_all(skins)
            db.session.commit()

    return app
