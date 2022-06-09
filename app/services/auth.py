import os

import db as Db
import jwt
import passlib.hash as Hash
import sqlalchemy.orm as orm
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import models, schemas

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
    return db.query(models.User).filter(models.User.username == username).first()


async def create_user(user: schemas.UserCreate, db: orm.Session, token: str = Depends(oauth2schema)):
    user_obj = models.User(username=user.username,
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


async def create_token(user: models.User):
    user_obj = schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {"access_token": token, "token_type": "Bearer"}


async def get_current_user(token: str = Depends(oauth2schema), db: orm.Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.User).get(payload["id"])
    except:
        raise HTTPException(
            status_code=401, detail="Invalid Username or Password")

    return schemas.User.from_orm(user)


async def update_user(user: schemas.User, username: str, password: str, new_username: str, new_password: str, db: orm.Session):
    if user.username != username:
        raise HTTPException(
            status_code=401, detail="Invalid Username")
    user_obj = await authenticate_user(username, password, db)
    if not user_obj:
        raise HTTPException(
            status_code=401, detail="Invalid Password")
    if new_username != "":
        user_obj.username = new_username
    if new_password != "":
        user_obj.hashed_password = Hash.bcrypt.hash(new_password)

    db.commit()


async def delete_user(user: schemas.User, username: str, password: str, db: orm.Session):
    if user.username != username:
        raise HTTPException(
            status_code=401, detail="Invalid Username")
    user_obj = await authenticate_user(username, password, db)
    if not user_obj:
        raise HTTPException(
            status_code=401, detail="Invalid Password")

    db.delete(user_obj)
    db.commit()
