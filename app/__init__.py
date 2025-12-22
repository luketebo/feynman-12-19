import os
import logging
from flask import Flask
from app.models import db
from dotenv import load_dotenv

load_dotenv()

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
    
    # 配置日志
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger.info(f"正在初始化费曼宠物应用 (Log Level: {log_level_str})...")

    # 数据库配置
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("未检测到 DATABASE_URL 环境变量！")
        raise ValueError("DATABASE_URL is not set")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = (log_level == logging.DEBUG)  # 仅在 DEBUG 模式下打印 SQL
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-key-123")

    db.init_app(app)
    logger.debug(f"数据库配置已加载: {db_url.split('@')[-1]}")

    # 应用前缀中间件
    app.wsgi_app = PrefixMiddleware(app.wsgi_app)
    logger.debug(f"已应用前缀中间件 (SCRIPT_NAME: {os.getenv('SCRIPT_NAME', '未设置')})")

    with app.app_context():
        from app.models import Skin
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.chat import chat_bp
        from app.routes.pet import pet_bp
        from app.routes.shop import shop_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(chat_bp)
        app.register_blueprint(pet_bp)
        app.register_blueprint(shop_bp)
        logger.info("所有路由蓝图已注册")

        try:
            logger.info("正在连接数据库并检查表结构 (db.create_all)...")
            db.create_all()
            logger.debug("数据库表结构检查/创建完成")
        except Exception as e:
            logger.error(f"数据库连接或创建表失败: {str(e)}")
            # 不直接抛出异常，尝试继续运行，或者你可以根据需要决定是否 raise
        
        # 初始化皮肤数据
        try:
            if not Skin.query.first():
                logger.info("检测到皮肤表为空，正在初始化默认皮肤...")
                skins = [
                    Skin(name="原始皮肤", price=0, description="最初的模样"),
                    Skin(name="小学霸", price=100, description="戴上眼镜，看起来更聪明了"),
                    Skin(name="小恐龙", price=500, description="嗷呜！我是最强学习者"),
                    Skin(name="宇航员", price=1000, description="向着知识的星辰大海出发")
                ]
                db.session.add_all(skins)
                db.session.commit()
                logger.info("默认皮肤初始化成功")
        except Exception as e:
            logger.error(f"初始化皮肤数据失败: {str(e)}")

    return app
