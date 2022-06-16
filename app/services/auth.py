import os

import db as Db
import jwt
import passlib.hash as Hash
import sqlalchemy.orm as orm
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import models as Models
from models import schemas as Schemas

load_dotenv()

oauth2schema = OAuth2PasswordBearer("/user/token")

JWT_SECRET = os.getenv('JWT_SECRET')


def get_db():
    db = Db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_username(username: str, db: orm.Session):
    return db.query(Models.User).filter(Models.User.username == username).first()


async def create_user(user: Schemas.UserCreate, db: orm.Session, token: str = Depends(oauth2schema)):
    user_obj = Models.User(username=user.username,
                           hashed_password=Hash.bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()

    return user_obj


async def authenticate_user(username: str, password: str, db: orm.Session):
    user = await get_user_by_username(username, db)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: Models.User):
    user_obj = Schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {"access_token": token, "token_type": "Bearer"}


async def get_current_user(token: str = Depends(oauth2schema), db: orm.Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(Models.User).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Invalid Username or Password")

    return Schemas.User.from_orm(user)


async def update_user(user: Schemas.User, password: str, new_username: str, new_password: str, db: orm.Session):
    user_obj = await authenticate_user(user.username, password, db)
    if not user_obj:
        raise HTTPException(
            status_code=401, detail="Invalid Password")
    if new_username != "":
        db_user = await get_user_by_username(new_username, db)
        if db_user:
            raise HTTPException(
                status_code=400, detail="Username already exists")
        user_obj.username = new_username
    if new_password != "":
        if password == new_password:
            raise HTTPException(
                status_code=400, detail="Password unchange")
        user_obj.hashed_password = Hash.bcrypt.hash(new_password)

    db.commit()


async def delete_user(user: Schemas.User, username: str, password: str, db: orm.Session):
    if user.username != username:
        raise HTTPException(
            status_code=401, detail="Invalid Username")
    user_obj = await authenticate_user(username, password, db)
    if not user_obj:
        raise HTTPException(
            status_code=401, detail="Invalid Password")

    db.delete(user_obj)
    db.commit()
