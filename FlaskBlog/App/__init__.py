import os
import uuid

from flask import Flask
from .views import blog, admin
from .exts import init_exts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    static_path = os.path.join(BASE_DIR, 'static')
    template_path = os.path.join(BASE_DIR, 'templates')
    print(static_path)
    # 静态文件和模板路径
    app = Flask(__name__, static_folder=static_path, template_folder=template_path)

    # 配置数据库
    db_uri = 'mysql+pymysql://root:root@localhost:3306/FlaskBlog'
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 设置秘钥
    app.config['SECRET_KEY'] = str(uuid.uuid4())
    # 注册蓝图
    app.register_blueprint(blueprint=blog)
    app.register_blueprint(blueprint=admin)

    # 初始化插件
    init_exts(app)
    return app
