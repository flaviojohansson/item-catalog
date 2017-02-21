from flask import Blueprint, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from app.database_setup import Base, Category, Handicraft, \
     HandicraftPicture, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('app/config/google_client_secret.json', 'r').read()
    )['web']['client_id']


# Connect to Database and create database session
engine = create_engine('sqlite:///thehandicrafter.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

handicraft = Blueprint('handicraft', __name__, url_prefix='/', template_folder='templates')


#
# User Helper Functions
#
def create_user(login_session):
    new_user = User(
                name=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture']
            )
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


#
# Login operations
#
# Create anti-forgery state token
@handicraft.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state)


# Disconnect based on provider
@handicraft.route('/logout')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            if 'credentials' in login_session:
                del login_session['credentials']

        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']

        flash('You have successfully been logged out')
        return redirect(url_for('front_page'))
    else:
        flash('You were not logged in')
        return redirect(url_for('front_page'))


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/{}/permissions?'
           'access_token={}'.format(facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return result


@handicraft.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # print "access token received %s " % access_token

    json_fb = json.loads(open('config/fb_client_secret.json', 'r').read())

    app_id = json_fb['web']['app_id']
    app_secret = json_fb['web']['app_secret']

    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&'
           'client_id={}&'
           'client_secret={}&'
           'fb_exchange_token={}'.format(app_id, app_secret, access_token))

    http = httplib2.Http()
    result = http.request(url, 'GET')[1]

    # Use token to get user info from API
    # userinfo_url = "https://graph.facebook.com/v2.8/me"

    # strip expire tag from access token
    token = result.split('&')[0]

    url = ('https://graph.facebook.com/v2.8/me?{}&'
           'fields=name,id,email'.format(token))

    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign
    # in our token
    stored_token = token.split('=')[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?{}&'
           'redirect=0&height=200&width=200'.format(token))

    result = http.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = login_session['username']
    flash("Now logged in as %s" % login_session['username'])
    return output


def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://accounts.google.com/o/oauth2/revoke?'
           'token={}'.format(access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@handicraft.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    print code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'config/google_client_secret.json',
            scope=''
        )
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print "falohou"
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
           'access_token={}'.format(access_token))

    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200
        )
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = login_session['username']
    flash("Now logged in as %s" % login_session['username'])
    return output


#
# Handicraft operations
#

# Create a new handicraft to show the world
@handicraft.route('/handicraft/create/', methods=['GET', 'POST'])
def create_handicraft():
    #if 'username' not in login_session:
    #    return redirect('/login')

    categories = session.query(Category).all()

    if request.method == 'POST':
        handicraft = Handicraft(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=3
            )
        session.add(handicraft)

        flash('New Restaurant {} Successfully Created'.format(handicraft.name))

        session.commit()

        return redirect(url_for('front_page'))

        #return redirect(url_for('read_handicraft', handicraft_id=handicraft.id))
    else:
        return render_template('handicraft/create.html', categories=categories)

# TODO colocar um decorator


# Show a handicraft
@handicraft.route('/handicraft/<int:handicraft_id>/')
def read_handicraft(handicraft_id):
    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()
    creator = getUserInfo(handicraft.user_id)

    #items = session.query(MenuItem).filter_by(
        #restaurant_id=restaurant_id).all()

    #if 'username' not in login_session or creator.id != login_session['user_id']:
    #    return render_template('publicmenu.html', items=items, restaurant=restaurant, creator=creator)
    #else:
    return render_template('handicraft/read.html', handicraft=handicraft)


# Edit a handicraft
@handicraft.route('/handicraft/<int:handicraft_id>/update', methods=['GET', 'POST'])
def update_handicraft(handicraft_id):
    editedRestaurant = session.query(
        Handicraft).filter_by(id=handicraft_id).one()

    if 'username' not in login_session:
        return redirect('/login')

    if editedRestaurant.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Handicraft Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('read_handicraft', handicraft_id=handicraft_id))
    else:
        return render_template('handicraft/update.html', handicraft=editedRestaurant)


# Delete a handicraft
@handicraft.route('/handicraft/<int:handicraft_id>/delete', methods=['GET', 'POST'])
def delete_handicraft(handicraft_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if restaurantToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('front_page'))
    else:
        return render_template('handicraft/delete.html', restaurant=restaurantToDelete)


# Show all categories
@handicraft.route('/category/JSON')
def category_JSON():
    categories = session.query(Category).order_by(Category.name).all()
    return jsonify(categories=[category.serialize for category in categories])


# Show the last handicrafts
@handicraft.route('/')
def front_page():
    handicrafts = session.query(Handicraft).order_by(Handicraft.created_at.desc())
    # Show the latest 10
    handicrafts = handicrafts.limit(10)
    return render_template('front_page.html', handicrafts=handicrafts)
