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

    # Initialise extensions
    # db.init_app(app)
    # migrate.init_app(app, db)
    # login_manager.init_app(app)
    # bcrypt.init_app(app)

    # Enable CORS
    CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

    # Test root route
    # @app.route('/', methods=['GET'])
    # def home():
    #     return jsonify({'message': 'Welcome to the Flask application!'})

    # @app.route("/test-session")
    # def test_session():
    #     from flask import session
    #     if "visits" in session:
    #         session["visits"] += 1
    #     else:
    #         session["visits"] = 1
    #     return jsonify({"visits": session["visits"]})

    # Register blueprints
    #from app.routes.api import api as api_bp
    #app.register_blueprint(api_bp, url_prefix='/api')
    from app.routes.file_handler import file_handler_bp
    from app.routes.users import users_bp
    from app.routes.main import pipeline_bp
    from app.routes.realtionship_summary import relationship_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(file_handler_bp)
    app.register_blueprint(relationship_bp)


    return app
