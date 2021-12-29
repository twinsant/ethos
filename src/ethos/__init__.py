# https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='Web3.0',
        DATABASE=os.path.join(app.instance_path, 'ethos.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, Web3.0!'

    from . import home
    app.register_blueprint(home.bp)

    from . import api
    app.register_blueprint(api.bp)


    return app