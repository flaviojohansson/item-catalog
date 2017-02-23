'''
Important functions for security management
'''

from string import letters
import random
import hashlib
import hmac


SECRET = 'yk6cE4oiPwEbS0tF'


def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, password, salt=None):
    if not salt:
        salt = make_salt()
    hexdigest = hashlib.sha256(name + password + salt).hexdigest()
    return '%s,%s' % (salt, hexdigest)


def valid_pw(name, password, hash):
    salt = hash.split(',')[0]
    return hash == make_pw_hash(name, password, salt)


def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
