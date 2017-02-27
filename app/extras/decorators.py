from functools import wraps
from flask import session as login_session
from flask import request, redirect, url_for
from urlparse import urlparse


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


def check_if_valid(class_name):
    '''Make sure the entity exists, based on class_name and
    the last method parameter
     Parameter:
        class_name: Datamodel name. e.g: Post, Comment'''

    def wrapper(func):
        def func_wrapper(self, *args):
            # Always the last parameter. Being post or comment

            # entity_id = args[-1]
            # key = db.Key.from_path(class_name, int(entity_id))
            # entity = db.get(key)

            # if entity:
            #     func(self, *args)  # Carry on
            # else:
            #     self.redirect('/')  # Smoothly goes to main page
            #     return
            func(self, *args)  # Carry on

        return func_wrapper
    return wrapper


def check_if_owner(class_name):
    '''Make sure the logged user is the owner of the entity
    Parameter:
        class_name: Datamodel name. e.g: Post, Comment'''

    def wrapper(func):
        def func_wrapper(self, *args):

            # # Always the last parameter. Being post or comment
            # entity_id = args[-1]
            # # In the other hand, the post_id is always the first
            # post_id = args[0]
            # key = db.Key.from_path(class_name, int(entity_id))
            # entity = db.get(key)
            # if self.user.key() == entity.user.key():
            #     func(self, *args)  # Carry on
            # else:
            #     # Always back to the related Post page, even for comments
            #     self.redirect('/post/%s' % str(post_id))
            #     return

            func(self, *args)  # Carry on

        return func_wrapper
    return wrapper
