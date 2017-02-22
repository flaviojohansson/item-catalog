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

from app.lib.decorators import login_required
from app.models.base import session
from app.models.handicraft import Handicraft
from app.models.category import Category


handicraft = Blueprint('handicraft', __name__)


#
# Handicraft operations
#

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
        session.add(handicraft)

        flash('New handicraft {} successfully created'.format(handicraft.name))

        session.commit()

        return redirect(url_for('read_handicraft', handicraft_id=handicraft.id))
    else:
        categories = session.query(Category).all()
        return render_template('handicraft/create.html', categories=categories)


# Show a handicraft
@handicraft.route('/<int:handicraft_id>/')
def read_handicraft(handicraft_id):
    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()
    return render_template('handicraft/read.html', handicraft=handicraft)


# Edit a handicraft
@handicraft.route('/handicraft/<int:handicraft_id>/update', methods=['GET', 'POST'])
@login_required
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
@handicraft.route('/<int:handicraft_id>/delete', methods=['GET', 'POST'])
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
