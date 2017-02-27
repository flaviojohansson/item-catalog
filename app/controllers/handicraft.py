from flask import Blueprint, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

from app.extras.decorators import login_required, must_exist, must_be_owner
from app.models.base import session
from app.models.handicraft import Handicraft
from app.models.category import Category


handicraft = Blueprint('handicraft', __name__)


# Create a new handicraft to show the world
@handicraft.route('/create/', methods=['GET', 'POST'])
@login_required
def create_handicraft():
    if request.method == 'POST':

        handicraft = Handicraft(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id']
            )

        if not handicraft.name:
            flash('Please give this handicraft a sweet name', 'error')
        if not handicraft.description:
            flash('Please tell more about your handicraft in the description', 'error')
        if int(handicraft.category_id) <= 0:
            flash('Please choose a category', 'error')

        # Stop if there are flash messages
        if '_flashes' in login_session:
            categories = session.query(Category).all()
            return render_template('handicraft/create.html',
                                   handicraft=handicraft,
                                   categories=categories)

        session.add(handicraft)

        flash(u'New handicraft {} successfully created'.format(handicraft.name), 'success')

        session.commit()

        return redirect(url_for('handicraft.read_handicraft', handicraft_id=handicraft.id))
    else:
        # Empty object so jinja template can handle
        handicraft = Handicraft()
        categories = session.query(Category).all()
        return render_template('handicraft/create.html',
                               handicraft=handicraft,
                               categories=categories)


# Show a handicraft
@handicraft.route('/<int:handicraft_id>')
@must_exist
def read_handicraft(handicraft_id):
    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()
    return render_template('handicraft/read.html', handicraft=handicraft)


# Show a handicraft in JSON format
@handicraft.route('/<int:handicraft_id>/JSON/')
@must_exist
def read_handicraft_JSON(handicraft_id):
    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()
    return jsonify(handicraft=[handicraft.serialize])


# Edit AND Delete a handicraft
@handicraft.route('/<int:handicraft_id>/update/', methods=['GET', 'POST'])
@login_required
@must_exist
@must_be_owner
def update_handicraft(handicraft_id):

    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()

    if request.method == 'POST':
        if ('action' in request.form) and (request.form['action'] == 'delete'):
            session.delete(handicraft)
            flash(u'Handicraft %s successfully deleted' % handicraft.name,
                  'success')
            session.commit()
            return redirect(url_for('home.front_page'))
        else:
            handicraft.name = request.form['name']
            handicraft.description = request.form['description']
            handicraft.category_id = request.form['category']

            if not handicraft.name:
                flash('Please give this handicraft a sweet name', 'error')
            if not handicraft.description:
                flash('Please tell more about your handicraft in the description', 'error')
            if int(handicraft.category_id) <= 0:
                flash('Please choose a category', 'error')

            # Stop if there are flash messages
            if '_flashes' in login_session:
                categories = session.query(Category).all()
                return render_template('handicraft/update.html',
                                       handicraft=handicraft,
                                       categories=categories)

            session.add(handicraft)
            flash(u'Handicraft {} successfully updated'.format(handicraft.name), 'success')
            session.commit()

            return redirect(url_for('handicraft.read_handicraft', handicraft_id=handicraft.id))
    else:
        categories = session.query(Category).all()
        return render_template('handicraft/update.html',
                               handicraft=handicraft,
                               categories=categories)
