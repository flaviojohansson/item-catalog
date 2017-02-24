from flask import Blueprint, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import asc
from flask import session as login_session
from flask import make_response
from app.models.base import session
from app.models.handicraft import Handicraft


home = Blueprint('home', __name__)


# Show the last handicrafts
@home.route('/')
def front_page():
    handicrafts = session.query(Handicraft).order_by(
        Handicraft.created_at.desc()
    )
    # Show the latest 10
    handicrafts = handicrafts.limit(30)
    return render_template('home/front_page.html', handicrafts=handicrafts)


@home.route('/list/category/<int:category_id>/')
def list_by_category():

    # handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()
    handicrafts = session.query(Handicraft) \
                  .filter_by(category_id=category_id) \
                  .order_by(Handicraft.created_at.desc())
    # Show the latest 10
    handicrafts = handicrafts.limit(30)
    return render_template('home/front_page.html', handicrafts=handicrafts)
