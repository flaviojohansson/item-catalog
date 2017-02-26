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


# Show the last handicrafts
@home.route('/')
def front_page():
    handicrafts = session.query(Handicraft).order_by(
        Handicraft.created_at.desc()
    )

    categories = session.query(Category).order_by(
        Category.name.desc()
    )

    # Show the latest 10
    handicrafts = handicrafts.limit(30)
    return render_template('home/front_page.html',
                           handicrafts=handicrafts,
                           categories=categories)


@home.route('/filter/category/<int:category_id>')
def list_by_category(category_id):
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
    return render_template('home/front_page.html',
                           handicrafts=handicrafts,
                           category=category,
                           categories=categories)


@home.route('/filter/user/<int:user_id>')
def list_by_user(user_id):
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
    return render_template('home/front_page.html',
                           handicrafts=handicrafts,
                           user=user,
                           categories=categories)


# Show all categories
@home.route('/category/JSON/')
def category_JSON():
    categories = session.query(Category).order_by(Category.name).all()
    return jsonify(categories=[category.serialize for category in categories])
