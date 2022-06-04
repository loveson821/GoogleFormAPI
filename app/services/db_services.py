import datetime as _dt
import fastapi as _fastapi
import fastapi.security as _security
from models import models as _models, schemas as _schemas
import sqlalchemy.orm as _orm

async def db_create_form(user: _schemas.User, db:_orm.Session, form:_schemas.FormCreate):
    form = _models.form(**form.dict(), owner_id=user.id)
    db.add(form)
    db.commit()
    return _schemas.Form.from_orm(form)

async def db_get_forms(user: _schemas.User, db:_orm.Session):
    forms = db.query(_models.form).filter_by(owner_id=user.id)

    return list(map(_schemas.Form.from_orm,forms))

async def _form_selector(form_id: str, user: _schemas.User, db:_orm.Session):
    form = db.query(_models.form).filter_by(owner_id=user.id).filter(_models.form.form_id == form_id).first()

    if form is None:
        raise _fastapi.HTTPException(status_code=401, detail="Form dose not exist")

    return form

async def db_get_form(form_id: str, user: _schemas.User, db:_orm.Session):
    form = await _form_selector(form_id, user, db)

    return _schemas.Form.from_orm(form)

async def db_delete_form(form_id: str, user: _schemas.User, db: _orm.Session):
    form = await _form_selector(form_id, user, db)
    form.deleted = True

    db.commit()

async def db_update_form(form_id: str, form: _schemas.FormCreate, user: _schemas.User, db: _orm.Session):
    form_db = await _form_selector(form_id, user, db)

    form_db.form_id = form.form_id
    form_db.link = form.link
    form_db.title = form.title
    form_db.text = form.text
    form_db.by = form.by
    form_db.date = form.date
    form_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()

    return _schemas.Form.from_orm(form_db)

