from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash
from flask_session import Session

from app import app
from app.route_helpers import login_required, apology, validate_user_data
from app.database_helpers import get_user_info, add_user, get_commutes


@app.route('/')
@login_required
def index():
    # Get all the commutes this user currently has
    commutes = get_commutes(session["user_id"])
    return render_template('index.html', commutes=commutes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    validation_result = validate_user_data('register', request)
    if not validation_result['passed']:
        return apology(validation_result['message'], validation_result['code'])

    # Query database for username
    if len(get_user_info(request.form.get("username"))) != 0:
        return apology('an acccount already exists for this username', 400)
    
    # Insert new user into the db with a hashed password
    add_user(request)
    
    return render_template("login.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Forget any user_id
    session.clear()

    if request.method == 'GET':
        return render_template('login.html')

    validation_result = validate_user_data('login', request)
    if not validation_result['passed']:
        return apology(validation_result['message'], validation_result['code'])

    # Query database for username
    rows = get_user_info(request.form.get("username"))

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
        return apology("invalid username and/or password", 403)

    # Remember which user has logged in
    session["user_id"] = rows[0][0]

    return redirect('/')


@app.route('/logout')
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")