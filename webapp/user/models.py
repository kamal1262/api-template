import datetime

from .. import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    status = db.Column(db.Boolean, nullable=False, default=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    email = db.Column(db.String(255))

    def __repr__(self):
        return "<User '{}'>".format(self.username)
