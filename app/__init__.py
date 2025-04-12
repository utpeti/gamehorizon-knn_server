import os
from dotenv import load_dotenv
from flask import Flask


def create_app(test_config=None):
    load_dotenv() 

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        MAIN_SERVER_API_BASE_URL=os.getenv('MAIN_SERVER_API_BASE_URL')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from .controllers import RecommendationController
    app.register_blueprint(RecommendationController.bp)

    return app