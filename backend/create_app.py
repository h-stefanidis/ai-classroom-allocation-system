from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_migrate import Migrate
# from flask_login import LoginManager
from flask_cors import CORS
from config import Config



# # Initialise extensions
# db = SQLAlchemy()
# migrate = Migrate()
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'  # Redirect to 'auth.login' when login is required
# bcrypt = Bcrypt()

def createApp(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
    from app.routes.file_handler import file_handler_bp
    from app.routes.users import users_bp
    from app.routes.main import pipeline_bp
    from app.routes.student_sna_anly import sna_bp
    from app.routes.realtionship_summary import relationship_bp


    app.register_blueprint(users_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(file_handler_bp)
    app.register_blueprint(relationship_bp)

    app.register_blueprint(sna_bp)
    app = Flask(__name__)

    return app
