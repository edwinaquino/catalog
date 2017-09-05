from functools import wraps
from flask import redirect
from flask import session as login_session

def login_check(f):
    ''' Determin if a user is logged in or not'''
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x
