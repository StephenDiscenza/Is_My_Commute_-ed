from flask import Flask
from app.database_helpers import setup_db

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set up the db
setup_db()