from flask import Flask, render_template, request
from database_helpers import update_station_ids

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Get the most recent data the stations
update_station_ids()
