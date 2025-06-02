# Recreate and rezip the fixed OAuth project due to environment reset

import os
import zipfile

from Main import socketio

base_dir = "/mnt/data/matty_app"
templates_dir = os.path.join(base_dir, "templates")
os.makedirs(templates_dir, exist_ok=True)

# home.html content
home_template = """{% extends "layout.html" %}
{% block content %}
  <h1>Welcome to Matty Social!</h1>
  {% if user %}
    <p>You are logged in as {{ user.email }}</p>
  {% else %}
    <p>This is a public view. Please <a href="{{ url_for('google.login') }}">log in with Google</a>.</p>
  {% endif %}
{% endblock %}
"""

# layout.html content
layout_template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Matty Social</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body class="funky1">
  <nav>
    <ul>
      <li><a href="{{ url_for('home') }}">Home</a></li>
      <li><a href="{{ url_for('logout') }}">Logout</a></li>
    </ul>
  </nav>
  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
"""

# app_oauth.py content
app_oauth_code = """from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = "google.login"

# OAuth setup
google_bp = make_google_blueprint(
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_CLIENT_SECRET",
    redirect_to="home"
)
app.register_blueprint(google_bp, url_prefix="/login")

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route("/")
def home():
    return render_template("home.html", user=current_user if current_user.is_authenticated else None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == '__main__':
    socketio.run(app, debug=True)
"""

# Write the files
with open(os.path.join(templates_dir, "home.html"), "w") as f:
    f.write(home_template)

with open(os.path.join(templates_dir, "layout.html"), "w") as f:
    f.write(layout_template)

with open(os.path.join(base_dir, "app_oauth.py"), "w") as f:
    f.write(app_oauth_code)

# Create the zip archive
zip_path = "/mnt/data/matty_app_oauth_home_fixed.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, base_dir)
            zipf.write(full_path, arcname)

zip_path

