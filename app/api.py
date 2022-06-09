from typing import List

import sqlalchemy.orm as orm
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

import db as Db
from models import schemas
from services import auth, db_services, form as Form

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
async def get_form(form_id: str, user: schemas.User = Depends(auth.get_current_user)):
    res = Form.get_form(form_id)
    return res


@app.get('/getresponses', status_code=200)
async def get_responses(form_id: str, user: schemas.User = Depends(auth.get_current_user)):
    res = Form.get_responses(form_id)
    return res


@app.post('/generate', status_code=200)
async def gen(form: schemas.genQuiz, user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    result = Form.create_form(form.docTitle, form.title, form.descr)
    id = result['formId']

    for q in form.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            Form.create_textQuestion(
                q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            Form.create_choiceQuestion(
                q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    form_create = schemas.FormCreate(
        form_id=result['formId'], link=result["responderUri"], title=form.title, text=form.descr, by=form.by, date=form.date)
    await db_services.db_create_form(user, db, form_create)
    return {"id": id, "link": result["responderUri"]}

# Users Authorization


@app.post("/user/create", status_code=200)
async def create_user(user: schemas.UserCreate, db: orm.Session = Depends(get_db)):
    db_user = await auth.get_user_by_username(user.username, db)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already exists")

    user_obj = await auth.create_user(user, db)

    return await auth.create_token(user_obj)


@app.post("/user/token", status_code=200)
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: orm.Session = Depends(get_db)):
    user = await auth.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await auth.create_token(user)


@app.get("/user/me", response_model=schemas.User, status_code=200)
async def get_user(user: schemas.User = Depends(auth.get_current_user)):
    return user


@app.put("/user/update", status_code=204)
async def update_user(username: str, password: str, new_username: str = "", new_password: str = "", user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    await auth.update_user(user, username, password, new_username, new_password, db)


@app.delete("/user/delete", status_code=204)
async def delete_user(username: str, password: str, user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    await auth.delete_user(user, username, password, db)


# @app.post("/forms", response_model=schemas.Form)
# async def db_create_form(form: schemas.FormCreate, user: schemas.User=Depends(auth.get_current_user), db:orm.Session=Depends(get_db)):
#     return await db_services.db_create_form(user, db, form)

@app.get("/forms", response_model=List[schemas.Form], status_code=200)
async def db_get_forms(user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    return await db_services.db_get_forms(user, db)


@app.get("/forms/{form_id}", status_code=200)
async def db_get_form(form_id: str, user: schemas.User = Depends(auth.get_current_user),  db: orm.Session = Depends(get_db)):
    return await db_services.db_get_form(form_id, user, db)


@app.delete("/forms/delete/{form_id}", status_code=204)
async def db_delete_form(form_id: str, user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    await db_services.db_delete_form(form_id, user, db)


@app.put("/form/update/{form_id}", status_code=204)
async def db_update_form(form_id: str, form: schemas.FormCreate, user: schemas.User = Depends(auth.get_current_user), db: orm.Session = Depends(get_db)):
    await db_services.db_update_form(form_id, form, user, db)


if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)
