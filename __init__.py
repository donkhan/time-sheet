import os

from flask import Flask

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'time_sheet.sqlite'),
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

from . import db
db.init_app(app)

from . import auth
app.register_blueprint(auth.bp)

from . import ts
app.register_blueprint(ts.bp)
app.add_url_rule('/', endpoint='ts.list')
    

# a simple page that says hello
@app.route('/hello')
def hello():
    return 'Hello, World!'

if __name__ == "__main__":  
    app.run()