from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from models import Notification

@app.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    for notif in notifs:
        notif.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)
