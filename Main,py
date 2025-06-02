from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_dance.contrib.google import make_google_blueprint, google
from flask_socketio import SocketIO
import os

# Allow OAuth over HTTP (not HTTPS) for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# === Flask App Setup ===
main = Flask(__name__)
main.config['SECRET_KEY'] = 'your-secret-key'
main.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# === Initialize Extensions ===
db = SQLAlchemy(main)
socketio = SocketIO(main, cors_allowed_origins="*")

login_manager = LoginManager(main)
login_manager.login_view = "google.login"

# === Google OAuth Blueprint ===
google_bp = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    redirect_to="home"
)
main.register_blueprint(google_bp, url_prefix="/home")

# === User Model ===
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Routes ===

@main.route("/")
def home():
    return render_template("home.html", user=current_user if current_user.is_authenticated else None)

@main.route("/login/google/authorized")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info", 400

    info = resp.json()
    email = info["email"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("home"))

@main.route("/post", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content")
    if content:
        post = Post(content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for("home"))

@main.route("/profile")
def profile():
    return render_template("profile.html")

@main.route("/feed")
def feed():
    return render_template("feed.html")

@main.route("/followers")
def followers():
    return render_template("followers.html")

@main.route("/following")
def following():
    return render_template("following.html")

@main.route("/terms")
def terms():
    return render_template("terms.html")

@main.route("/privacy")
def privacy():
    return render_template("privacy.html")

@main.route("/login")
def login():
    return render_template("login.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# === Start the Server ===
if __name__ == '__main__':
    socketio.run(main, debug=True)

