import datetime

import db as Db
import passlib.hash as Hash
import sqlalchemy as sa
import sqlalchemy.orm as orm


class User(Db.Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, unique=True, index=True)
    hashed_password = sa.Column(sa.String)

    fomrs = orm.relationship("form", back_populates="owner")

    def verify_password(self, password: str):
        return Hash.bcrypt.verify(password, self.hashed_password)


class form(Db.Base):
    __tablename__ = "forms"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    form_id = sa.Column(sa.String, index=True)
    link = sa.Column(sa.String, index=True)
    title = sa.Column(sa.String, index=True)
    text = sa.Column(sa.String, index=True)
    by = sa.Column(sa.String, index=True, default="")
    deleted = sa.Column(sa.Boolean, default=False)
    date = sa.Column(sa.String, default="")
    date_created = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    date_last_updated = sa.Column(
        sa.DateTime, default=datetime.datetime.utcnow)

    owner = orm.relationship("User", back_populates="fomrs")
