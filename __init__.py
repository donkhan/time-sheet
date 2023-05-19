import os

from flask import Flask



# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, '/home/kamilukrizq/time-sheet/instance/time_sheet.sqlite'),
)



# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

import db
db.init_app(app)

import auth
app.register_blueprint(auth.bp)

import ts
app.register_blueprint(ts.bp)


# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

    return app