from flask import redirect, render_template, request, session, Response
from werkzeug.security import check_password_hash
from flask_session import Session
import json

from app import app
from app.route_helpers import login_required, apology, validate_user_data, add_commute_helper
from app.database_helpers import get_user_info, add_user, get_commutes, get_leg_data, get_stations_by_line, add_commute_to_db, delete_commute_from_db
from app.mta_data_helpers import get_commute_alets, analyze_commute_alerts


LINES = ['1', '2', '3', '4', '5', '6', '7', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'J', 'L', 'M', 'N', 'Q', 'R', 'S', 'W', 'Z']

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
        commute_id = request_json['commute_id']
        app.logger.info(f"Recieved request: {request_json}")
    except Exception as e:
        app.logger.error(e)
        response = json.dumps({'error': f'Failed to get the body of the request with error {e}'})
        return Response(response, 400, mimetype='application/json')
    # Get a list of the alert data for all lines included in the commute
    commute_alerts_text = get_commute_alets(commute_id)
    # Use the alert data to determine whether the commute is bad
    commute_is_bad = analyze_commute_alerts(commute_alerts_text)
    response = json.dumps({'result': commute_is_bad, 'alerts': commute_alerts_text})
    return Response(response, 200, mimetype='application/json')


@app.route('/addcommute', methods=['GET', 'POST'])
@login_required
def add_commute():
    if request.method == 'GET':
        return render_template('new_commute.html', lines=LINES)
    
    success, response = add_commute_helper(request)
    # if everything went well we get back True for sucess and None for the response
    if success:
        return redirect('/')
    else:
        return Response(response, 400, mimetype='application/json')


@app.route('/begineditcommute', methods=['POST'])
@login_required
def begin_edit_commute():
    # Here the user is saying I want to update the commute with the supplied id. We return the html giving the user that ability
    commute_id = request.form.get('commute_id')
    commute_name = request.form.get('commute_name')
    # Get all the leg data for the commute and construct JSON used by the template
    legs = [dict(leg) for leg in get_leg_data(commute_id)]
    for idx, leg in enumerate(legs):
        stations_sql_data = get_stations_by_line(leg['line'])
        stations = [{'name': station['stop_name'], 'value': station['gtfs_stop_id'] + '|' + station['stop_name']} for station in stations_sql_data]
        leg['stations'] = stations
        leg['line_name_id'] = f'line{idx + 1}'
        leg['origin_name_id'] = f'origin_name{idx + 1}'
        leg['termination_name_id'] = f'termination_name{idx + 1}'
        leg['origin_value'] = leg['origin_id'] + '|' + leg['origin_name']
        leg['termination_value'] = leg['termination_id'] + '|' + leg['termination_name']
        leg['idx'] = str(idx + 1)
    commute_data = {
        'id': commute_id,
        'name': commute_name,
        'legs': legs
    }
    return render_template('edit_commute.html', commute_data=commute_data, lines=LINES)


@app.route('/editcommute', methods=['POST', 'GET'])
@login_required
def edit_commute():    
    # This is our update. Instead of trying to find an update all these ids, it's simpler to just delete the old commute and add this as a new one
    commute_id = request.form.get('commute_id')
    delete_commute_from_db(commute_id)
    success, response = add_commute_helper(request)
    # if everything went well we get back True for sucess and None for the response
    if success:
        return redirect('/')
    else:
        return Response(response, 400, mimetype='application/json')


@app.route('/deletecommute', methods=['POST'])
@login_required
def delete_commute():
    commute_id = request.form.get('commute_id')
    delete_commute_from_db(commute_id)
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