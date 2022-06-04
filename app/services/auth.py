import fastapi as _fastapi
import fastapi.security as _security
from models import models as _models, schemas as _schemas
import db as _db
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt

from dotenv import load_dotenv
import os
load_dotenv()

oauth2schema = _security.OAuth2PasswordBearer("/user/token")

JWT_SECRET = os.getenv('JWT_SECRET')

def get_db():
    db = _db.SessionLocal()
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