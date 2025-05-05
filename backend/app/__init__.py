# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    @app.route('/')
    def home():
        return {'message': 'AI Classroom Allocation System is running'}

    # You can add blueprints or routes here
    # from .routes import example_blueprint
    # app.register_blueprint(example_blueprint)

    return app