from flask import Flask
from config import Config
from app.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.main import main_bp
    from app.routes.groups import groups_bp
    from app.routes.teachers import teachers_bp
    from app.routes.subjects import subjects_bp
    from app.routes.lessons import lessons_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(groups_bp, url_prefix="/groups")
    app.register_blueprint(teachers_bp, url_prefix="/teachers")
    app.register_blueprint(subjects_bp, url_prefix="/subjects")
    app.register_blueprint(lessons_bp)

    from app import cli
    cli.register_cli(app)

    from app import models  # noqa: F401

    return app