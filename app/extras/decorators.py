from functools import wraps
from flask import session as login_session
from flask import request, redirect, url_for
from urlparse import urlparse
from app.models.base import session
from app.models.handicraft import Handicraft


def login_required(func):
    '''Not logged users are redirect to the login page and then
    redirected back to the original page'''

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        if 'username' not in login_session:
            # use flask session, no cookies or url parameters needed
            url = urlparse(request.url)
            login_session['redirect'] = ''.join([url.path, url.params])
            return redirect(url_for('auth.signin'))
        return func(*args, **kwargs)  # Carry on

    return func_wrapper


def must_exist(func):
    '''Make sure the handicraft exists otherwise redirect the user'''

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        handicraft = session.query(Handicraft).filter_by(
            id=kwargs['handicraft_id']
        ).first()

        if not handicraft:
            return redirect(url_for('home.front_page'))
        return func(*args, **kwargs)  # Carry on

    return func_wrapper


def must_be_owner(func):
    '''Make sure the the user logged is the owner of the handicraft.
    Assumes user is logged and the handicraft exists'''

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        handicraft = session.query(Handicraft).filter_by(
            id=kwargs['handicraft_id']
        ).first()

        if login_session['user_id'] != handicraft.user_id:
            return redirect(url_for('handicraft.read_handicraft',
                                    handicraft_id=handicraft.id))
        return func(*args, **kwargs)  # Carry on

    return func_wrapper
