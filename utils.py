def create_notification(user_id, message, db, Notification):
    notif = Notification(user_id=user_id, message=message)
    db.session.add(notif)
    db.session.commit()
