import datetime as _dt

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash

import database as _database
import services as _services
_services.utc2local()

class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    username = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)

    fomrs = _orm.relationship("form", back_populates="owner")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class form(_database.Base):
    __tablename__ = "forms"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))
    form_id = _sql.Column(_sql.String, index=True)
    link = _sql.Column(_sql.String, index=True)
    title = _sql.Column(_sql.String, index=True)
    by = _sql.Column(_sql.String, index=True, default="")
    date = _sql.Column(_sql.String, default="")
    date_created = _sql.Column(_sql.DateTime, default=_services.utc2local(_dt.datetime.utcnow))
    date_last_updated = _sql.Column(_sql.DateTime, default=_services.utc2local(_dt.datetime.utcnow))

    owner = _orm.relationship("User", back_populates="fomrs")