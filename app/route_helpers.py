from flask import session, redirect, render_template
from functools import wraps



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
