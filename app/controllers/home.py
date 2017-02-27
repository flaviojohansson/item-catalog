from flask import Blueprint, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import asc
from flask import session as login_session
from flask import make_response
from app.models.base import session
from app.models.handicraft import Handicraft
from app.models.category import Category
from app.models.user import User


home = Blueprint('home', __name__)


def jsonify_handicrafts(handicrafts):
    'Returs the JSON format of handicrafts'
    return jsonify(handicrafts=[
        handicraft.serialize for handicraft in handicrafts
    ])


def list_by_category_or_JSON(category_id, json_output):
    # with first() category will be None if no rows found
    category = session.query(Category).filter_by(id=category_id).first()
    if not category:
        return redirect(url_for('home.front_page'))
    categories = session.query(Category).order_by(
        Category.name.desc()
    )
    handicrafts = session.query(Handicraft) \
        .filter_by(category_id=category_id) \
        .order_by(Handicraft.created_at.desc())
    # Show the latest 10
    handicrafts = handicrafts.limit(30)

    if json_output:
        return jsonify_handicrafts(handicrafts)
    else:
        return render_template('home/front_page.html',
                               handicrafts=handicrafts,
                               category=category,
                               categories=categories)


def list_by_user_or_JSON(user_id, json_output):
    # with first() user will be None if no rows found
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return redirect(url_for('home.front_page'))
    categories = session.query(Category).order_by(
        Category.name.desc()
    )
    handicrafts = session.query(Handicraft) \
        .filter_by(user_id=user_id) \
        .order_by(Handicraft.created_at.desc())
    # Show the latest 10
    handicrafts = handicrafts.limit(30)

    if json_output:
        return jsonify_handicrafts(handicrafts)
    else:
        return render_template('home/front_page.html',
                               handicrafts=handicrafts,
                               user=user,
                               categories=categories)


# Show the last handicrafts
@home.route('/')
def front_page():
    handicrafts = session.query(Handicraft).order_by(
        Handicraft.created_at.desc()
    )
    categories = session.query(Category).order_by(
        Category.name.desc()
    )
    # Show the latest 30
    handicrafts = handicrafts.limit(30)
    return render_template('home/front_page.html',
                           handicrafts=handicrafts,
                           categories=categories)


# Show the last handicrafts
@home.route('/signedin')
def signedin():
    # session redirect is set at login decorators, so after sucessfully
    # signing in, the user is redirected here. This way we avoid cookies
    if 'redirect' in login_session:
        uri = login_session['redirect']
        del login_session['redirect']  # clean session value
        return redirect(uri)
    return redirect(url_for('home.front_page'))

# Show the last 30 handicrafts, in JSON format
@home.route('/JSON/')
def front_page_JSON():
    handicrafts = session.query(Handicraft).order_by(
        Handicraft.created_at.desc()
    )
    # Show the latest 30
    handicrafts = handicrafts.limit(30)
    return jsonify_handicrafts(handicrafts)


# List all handicrafts by category
@home.route('/filter/category/<int:category_id>')
def filter_by_category(category_id):
    return list_by_category_or_JSON(category_id, False)


# List all handicrafts by category, in JSON format
@home.route('/filter/category/<int:category_id>/JSON/')
def filter_by_category_JSON(category_id):
    return list_by_category_or_JSON(category_id, True)


# List all handicrafts by user
@home.route('/filter/user/<int:user_id>')
def filter_by_user(user_id):
    return list_by_user_or_JSON(user_id, False)


# List all handicrafts by user, in JSON format
@home.route('/filter/user/<int:user_id>/JSON/')
def filter_by_user_JSON(user_id):
    return list_by_user_or_JSON(user_id, True)


# Show all categories
@home.route('/category/JSON/')
def category_JSON():
    categories = session.query(Category).order_by(Category.name).all()
    return jsonify(categories=[category.serialize for category in categories])
