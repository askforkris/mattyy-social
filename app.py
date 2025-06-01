import os
from dotenv import load_dotenv
import os


from models import db
from routes_notifications import notifications
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from flask_socketio import SocketIO



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*")


app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = "google.login"

load_dotenv()


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === ROUTES ===

# Home route — works with or without login
@app.route("/")
def home():
    return render_template("home.html", user=current_user if current_user.is_authenticated else None)

# Google login callback
@app.route("/login/google/authorized")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info", 400

    info = resp.json()
    email = info["email"]

    # Create or get user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("home"))

@app.route("/post", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content")
    if content:
        post = Post(content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for("home"))


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)