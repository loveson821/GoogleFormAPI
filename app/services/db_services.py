import datetime

import sqlalchemy.orm as orm
from fastapi import HTTPException
from models import models as Models
from models import schemas as Schemas


async def db_create_form(user: Schemas.User, db: orm.Session, form: Schemas.FormCreate):
    form = Models.form(**form.dict(), owner_id=user.id)
    db.add(form)
    db.commit()
    return Schemas.Form.from_orm(form)


async def db_get_forms(user: Schemas.User, db: orm.Session):
    forms = db.query(Models.form).filter_by(owner_id=user.id)

    return list(map(Schemas.Form.from_orm, forms))


async def _form_selector(form_id: str, user: Schemas.User, db: orm.Session):
    form = db.query(Models.form).filter_by(owner_id=user.id).filter(
        Models.form.form_id == form_id).first()

    if form is None:
        raise HTTPException(
            status_code=401, detail="Form dose not exist")

    return form


async def db_get_form(form_id: str, user: Schemas.User, db: orm.Session):
    form = await _form_selector(form_id, user, db)

    return Schemas.Form.from_orm(form)


async def db_delete_form(form_id: str, user: Schemas.User, db: orm.Session):
    form = await _form_selector(form_id, user, db)
    form.deleted = True
    form.date_last_updated = datetime.datetime.utcnow()

    db.commit()


async def db_update_form(form_id: str, form: Schemas.FormCreate, user: Schemas.User, db: orm.Session):
    form_db = await _form_selector(form_id, user, db)

    form_db.form_id = form.form_id
    form_db.link = form.link
    form_db.title = form.title
    form_db.text = form.text
    form_db.by = form.by
    form_db.date = form.date
    form_db.date_last_updated = datetime.datetime.utcnow()

    db.commit()

    return Schemas.Form.from_orm(form_db)
