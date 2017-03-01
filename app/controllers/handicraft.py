from flask import Blueprint, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from flask import send_from_directory
import random
import string
import config
import os
import uuid
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from werkzeug.utils import secure_filename

from app.extras.decorators import login_required, must_exist, must_be_owner
from app.models.base import session
from app.models.handicraft import Handicraft
from app.models.handicraft_picture import HandicraftPicture
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
    return render_template('handicraft/read.html',
                           handicraft=handicraft)


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
    categories = session.query(Category).all()

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
                return render_template('handicraft/update.html',
                                       handicraft=handicraft,
                                       categories=categories)

            session.add(handicraft)
            flash(u'Handicraft {} successfully updated'.format(handicraft.name), 'success')
            session.commit()

            return redirect(url_for('handicraft.read_handicraft', handicraft_id=handicraft.id))
    else:
        return render_template('handicraft/update.html',
                               handicraft=handicraft,
                               categories=categories)


@handicraft.route('/picture/<string:file_name>', methods=['GET'])
def read_image(file_name):
    return send_from_directory(os.path.join(config.UPLOAD_FOLDER), file_name)


# Helper function 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# Upload OR Delete a picture to some handicraft
# As seen at http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
# The ideal would be upload using HTML5 and stuff...
@handicraft.route('/<int:handicraft_id>/picture/', methods=['POST'])
@login_required
@must_exist
@must_be_owner
def upload_image(handicraft_id):

    handicraft = session.query(Handicraft).filter_by(id=handicraft_id).one()

    if ('image' not in request.files) or (request.files['image'].filename == ''):
        flash('Please choose a picture to import', 'error')

    image = request.files['image']

    # Give the new file a unique name
    file_name = ''.join([
            str(uuid.uuid4()),
            os.path.splitext(image.filename)[-1]])

    print file_name

    # Stop if there are flash messages
    if '_flashes' not in login_session:
        if image and allowed_file(image.filename):
            full_path = os.path.join(
                            config.UPLOAD_FOLDER,
                            secure_filename(file_name))
            image.save(full_path)

            handicraft_picture = HandicraftPicture(
                file_name=file_name,
                handicraft_id=handicraft.id)

            session.add(handicraft_picture)
            session.commit()

    return redirect(url_for('handicraft.update_handicraft',
                            handicraft_id=handicraft.id))


@handicraft.route('/<int:handicraft_id>/picture/<int:picture_id>/delete',
                  methods=['POST'])
@login_required
@must_exist
@must_be_owner
def delete_image(handicraft_id, picture_id):

    handicraft_picture = session.query(HandicraftPicture).filter_by(
        id=picture_id,
        handicraft_id=handicraft_id).first()

    if handicraft_picture:
        if ('action' in request.form) and (request.form['action'] == 'delete'):
            # Delete the file
            os.remove(os.path.join(config.UPLOAD_FOLDER,
                                   handicraft_picture.file_name))
            # Delete the registry in the database
            session.delete(handicraft_picture)
            flash(u'Picture successfully deleted', 'success')
            session.commit()

    return redirect(url_for('handicraft.update_handicraft',
                            handicraft_id=handicraft_id))
