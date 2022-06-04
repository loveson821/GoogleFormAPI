import datetime as _dt
import fastapi as _fastapi
import fastapi.security as _security
import database as _database
from models import models as _models, schemas as _schemas
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt

oauth2schema = _security.OAuth2PasswordBearer("/user/token")

JWT_SECRET = "TEST"

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_user_by_username(username: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.username == username).first()

async def create_user(user: _schemas.UserCreate, db: _orm.Session, token: str=_fastapi.Depends(oauth2schema)):
    user_obj = _models.User(username=user.username, hashed_password=_hash.bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()

    return user_obj

async def authenticate_user(username: str, password: str, db: _orm.Session):
    user = await get_user_by_username(username, db)

    if not user:
        return False
    
    if not user.verify_password(password):
        return False

    return user

async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)

    token = _jwt.encode(user_obj.dict(), JWT_SECRET)

    return {"access_token": token, "token_type": "Bearer"}

async def get_current_user(token: str = _fastapi.Depends(oauth2schema), db: _orm.Session=_fastapi.Depends(get_db)):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Username or Password")

    return _schemas.User.from_orm(user)

async def update_user(user: _schemas.User, username: str, password: str, new_username: str, new_password: str, db: _orm.Session):
    if user.username != username:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Username")
    user_obj = await authenticate_user(username, password, db)
    if not user_obj:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Password")    
    if new_username!="":
        user_obj.username = new_username
    if new_password!="":
        user_obj.hashed_password = _hash.bcrypt.hash(new_password)

    db.commit()

async def delete_user(user: _schemas.User, username: str, password: str, db:_orm.Session):
    if user.username != username:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Username")
    user_obj = await authenticate_user(username, password, db)
    if not user_obj:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Password")  

    
    db.delete(user_obj)
    db.commit()

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

    db.delete(form)
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

