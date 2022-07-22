from flask import redirect, render_template, request, session, Response
from werkzeug.security import check_password_hash
from flask_session import Session
import json

from app import app
from app.route_helpers import login_required, apology, validate_user_data
from app.database_helpers import get_user_info, add_user, get_commutes, get_leg_data, get_stations_by_line, add_commute_to_db


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
    if len(rows) != 1 or not check_password_hash(rows[0]['hash'], request.form.get("password")):
        return apology("invalid username and/or password", 403)

    # Remember which user has logged in
    session["user_id"] = rows[0]['id']

    return redirect('/')


@app.route('/logout')
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route('/checkcommute', methods=['POST'])
@login_required
def check_commute():
    '''Checks live and historical data to determine a likely delay for the given commute'''
    try:
        request_json = request.get_json()
        app.logger.info(f"Recieved request: {request_json}")
    except Exception as e:
        app.logger.error(e)
        response = json.dumps({'error': f'Failed to get the body of the request with error {e}'})
        return Response(response, 400, mimetype='application/json')
    # Get origin and destination data for each leg of the commute from the db
    commute_legs = get_leg_data(request['commute_id'])
    for leg in commute_legs:
        # Get live data for line this leg uses
        # Add at least one commute to the db before trying this part
        pass


@app.route('/addcommute', methods=['GET', 'POST'])
@login_required
def add_commute():
    if request.method == 'GET':
        lines = ['1', '2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'J', 'L', 'M', 'N', 'Q', 'R', 'S', 'W', 'Z']
        return render_template('new_commute.html', lines=lines)
    
    # For a post request we need to create the JSON expected by the add_commute function from the data in the form
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
        return Response(response, 400, mimetype='application/json')
    
    return redirect('/')


@app.route('/getstations')
def get_stations():
    args = request.args
    try:
        line = args.get('line')
    except Exception as e:
        app.logger.error(e)
        response = json.dumps({'error': 'Failed to get the "line" parameter from the request'})
        return Response(response, 400, mimetype='application/json')
    stations_sql_data = get_stations_by_line(line) # This is a list of sqlite3 row objects and we want a list of dicts
    stations = []
    for station in stations_sql_data:
        stations.append({'name': station['stop_name'], 'id': station['gtfs_stop_id']})
    return Response(json.dumps(stations), 200, mimetype='application/json')