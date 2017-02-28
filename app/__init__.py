from flask import Flask, render_template, request, abort, session
from flask_debugtoolbar import DebugToolbarExtension
from os import path
from jinja2 import Markup
import random, string

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


# Add a custom jinja filter that converts newlines to <br>
@app.template_filter()
def nl2br(value):
    # Markup makes the value safe as in the filter safe
    return Markup(value.replace('\n', '<br>'))


# CSRF Protection
# As seen at http://flask.pocoo.org/snippets/3/
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if (not token or (token != request.form.get('_csrf_token') and
           token != request.args.get('_csrf_token'))):
            abort(403)


def generate_csrf_token():
    # Should I use openssl_random_pseudo_bytes ??
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(64)
        )
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token
