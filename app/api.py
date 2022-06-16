from typing import List

import sqlalchemy.orm as orm
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

import db as Db
from models import schemas as Schemas
from services import auth as Auth
from services import db_services as Db_services
from services import form as Form
from services import rss as Rss

tags_metadata = [
    {
        "name": "",
        "description": ""
    }
]

app = FastAPI(openapi_tags=tags_metadata)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = Db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create GoogleForm


@app.get('/getform', status_code=200)
async def get_form(form_id: str, user: Schemas.User = Depends(Auth.get_current_user)):
    res = Form.get_form(form_id)
    return res


@app.get('/getresponses', status_code=200)
async def get_responses(form_id: str, user: Schemas.User = Depends(Auth.get_current_user)):
    res = Form.get_responses(form_id)
    return res


@app.post('/generate', status_code=200)
async def gen(form: Schemas.genQuiz, user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
    result = Form.create_form(form.docTitle, form.title, form.text)
    id = result['formId']

    req = {}
    req['requests'] = Form.gen_req(form.dict())

    Form.create_items(req, id)
    form_create = Schemas.FormCreate(
        form_id=result['formId'], link=result["responderUri"], title=form.title, text=form.text, by=form.by, date=form.date)
    await Db_services.db_create_form(user, db, form_create)
    return {"id": id, "link": result["responderUri"]}

# Users Authorization


@app.post("/user/create", status_code=200)
async def create_user(user: Schemas.UserCreate, db: orm.Session = Depends(get_db)):
    db_user = await Auth.get_user_by_username(user.username, db)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already exists")

    user_obj = await Auth.create_user(user, db)

    return await Auth.create_token(user_obj)


@app.post("/user/token", status_code=200)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: orm.Session = Depends(get_db)):
    user = await Auth.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await Auth.create_token(user)


@app.get("/user/me", response_model=Schemas.User, status_code=200)
async def get_user(user: Schemas.User = Depends(Auth.get_current_user)):
    return user


@app.post("/user/update", status_code=204)
async def update_user(update: Schemas.UserUpdate, user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
    await Auth.update_user(user, update.password, update.new_username, update.new_password, db)


@app.delete("/user/delete", status_code=204)
async def delete_user(username: str, password: str, user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
    await Auth.delete_user(user, username, password, db)


@app.get("/forms", response_model=List[Schemas.Form], status_code=200)
async def db_get_forms(user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
    return await Db_services.db_get_forms(user, db)


@app.get("/forms/{form_id}", status_code=200)
async def db_get_form(form_id: str, user: Schemas.User = Depends(Auth.get_current_user),  db: orm.Session = Depends(get_db)):
    return await Db_services.db_get_form(form_id, user, db)


@app.delete("/forms/delete/{form_id}", status_code=204)
async def db_delete_form(form_id: str, user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
    await Db_services.db_delete_form(form_id, user, db)


# @app.put("/form/update/{form_id}", status_code=204)
# async def db_update_form(form_id: str, form: Schemas.FormCreate, user: Schemas.User = Depends(Auth.get_current_user), db: orm.Session = Depends(get_db)):
#     await Db_services.db_update_form(form_id, form, user, db)


# Rss Feed
@app.get('/rss', status_code=200)
async def rss(url: str, limit: int=999, detail: bool=False):
    res = Rss.rss(url=url, limit=limit, detail=detail)
    return res


if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)
