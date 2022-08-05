from flask import session, redirect, render_template
from functools import wraps
import json
from app import app

from .database_helpers import add_commute_to_db


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def validate_user_data(type, request):
    '''
    Checks for the existance and validity of login or registration data.
    Returns a dict of the form: {passed: bool, message: str, code: int}
    '''
    result = {}
    # Ensure username was submitted
    if not request.form.get("username"):
        result['passed'] = False
        result['message'] = "must provide username"
        result['code'] = 403
        return result

    # Ensure password was submitted
    if not request.form.get("password"):
        result['passed'] = False
        result['message'] = "must provide password"
        result['code'] = 403
        return result
    
    # When registering 
    if type == 'register':
        # Ensure a password confirmation is provided
        if not request.form.get('confirmPassword'):
            result['passed'] = False
            result['message'] = "must provide a confirmation of the password"
            result['code'] = 403
            return result
        
        # Ensure the password and the confirmation match
        if request.form.get('password') != request.form.get('confirmPassword'):
            result['passed'] = False
            result['message'] = "the password and the password confirmation must match"
            result['code'] = 403
            return result
    
    result['passed'] = True
    return result
    

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def add_commute_helper(request):
    request_json = {'user_id': session['user_id'], 'name': request.form.get('name'), 'legs': []}
    leg_index = 1
    while True:
        leg = {}
        leg['line'] = request.form.get(f'line{leg_index}')
        try: 
            origin_info = request.form.get(f'origin_name{leg_index}').split('|') # data is a string with the format "origin_id|origin_name"
        except AttributeError:
            break
        leg['originId'] = origin_info[0]
        leg['originName'] = origin_info[1]
        termination_info = request.form.get(f'termination_name{leg_index}').split('|')
        leg['terminationId'] = termination_info[0]
        leg['terminationName'] = termination_info[1]
        request_json['legs'].append(leg)
        leg_index += 1 
    try:
        add_commute_to_db(request_json)
    except Exception as e:
        app.logger.error(e)
        response = json.dumps({'error': f'Adding commute record failed'})
        return False, response
    return True, None