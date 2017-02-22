from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from os import path
# Blueprint
from app.controllers.home import home
from app.controllers.auth import auth
from app.controllers.handicraft import handicraft

template_folder = path.join(path.abspath(path.dirname(__file__)), 'templates')
static_folder = path.join(path.abspath(path.dirname(__file__)), 'static')

app = Flask('TheHandicrafter',
            template_folder=template_folder,
            static_folder=static_folder)


app.config.from_pyfile('config.py')

# toolbar = DebugToolbarExtension(app)

# Register all blueprints
app.register_blueprint(home)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(handicraft, url_prefix='/handicraft')


# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
