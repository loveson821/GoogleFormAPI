import uvicorn
from models import schemas as _schemas
import fastapi as _fastapi
from fastapi.middleware.cors import CORSMiddleware
import fastapi.security as _security
from typing import List
import sqlalchemy.orm as _orm
from services import db_services as _db_servicess, form as _form, auth as _auth
import db as _db

tags_metadata = [
    {
        "name": "",
        "description": ""
    }
]

app = _fastapi.FastAPI(openapi_tags=tags_metadata)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = _db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create GoogleForm
@app.get('/getform', status_code=200)
async def get_form(form_id: str, user: _schemas.User = _fastapi.Depends(_auth.get_current_user)):
    res = _form.get_form(form_id)
    return res

@app.get('/getresponses', status_code=200)
async def get_responses(form_id: str, user: _schemas.User = _fastapi.Depends(_auth.get_current_user)):
    res = _form.get_responses(form_id)
    return res

@app.post('/generate', status_code=200)
async def gen(form: _schemas.genQuiz, user: _schemas.User = _fastapi.Depends(_auth.get_current_user), db: _orm.Session = _fastapi.Depends(get_db)):
    result = _form.create_form(form.docTitle, form.title, form.descr)
    id = result['formId']

    for q in form.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            _form.create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            _form.create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    form_create = _schemas.FormCreate(form_id=result['formId'], link=result["responderUri"],title=form.title,text=form.descr,by=form.by,date=form.date)
    await _db_servicess.db_create_form(user, db, form_create)
    return {"id": id, "link": result["responderUri"]}

# Users Authorization
@app.post("/user/create", status_code=200)
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    db_user = await _auth.get_user_by_username(user.username, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Username already exists")
    
    user_obj = await _auth.create_user(user, db)

    return await _auth.create_token(user_obj)

@app.post("/user/token", status_code=200)
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(), db: _orm.Session = _fastapi.Depends(get_db)):
    user = await _auth.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _auth.create_token(user)

@app.get("/user/me", response_model=_schemas.User, status_code=200)
async def get_user(user: _schemas.User = _fastapi.Depends(_auth.get_current_user)):
    return user

@app.put("/user/update", status_code=204)
async def update_user(username: str, password: str, new_username: str="", new_password: str="", user: _schemas.User = _fastapi.Depends(_auth.get_current_user), db: _orm.Session = _fastapi.Depends(get_db)):
    await _auth.update_user(user, username, password, new_username, new_password, db)

@app.delete("/user/delete", status_code=204)
async def delete_user(username: str, password: str, user: _schemas.User = _fastapi.Depends(_auth.get_current_user), db: _orm.Session = _fastapi.Depends(get_db)):
    await _auth.delete_user(user, username, password, db)


# @app.post("/forms", response_model=_schemas.Form)
# async def db_create_form(form: _schemas.FormCreate, user: _schemas.User=_fastapi.Depends(_auth.get_current_user), db:_orm.Session=_fastapi.Depends(get_db)):
#     return await _db_servicess.db_create_form(user, db, form)

@app.get("/forms", response_model=List[_schemas.Form], status_code=200)
async def db_get_forms(user: _schemas.User=_fastapi.Depends(_auth.get_current_user), db:_orm.Session=_fastapi.Depends(get_db)):
    return await _db_servicess.db_get_forms(user, db)

@app.get("/forms/{form_id}", status_code=200)
async def db_get_form(form_id: str, user: _schemas.User=_fastapi.Depends(_auth.get_current_user), db:_orm.Session=_fastapi.Depends(get_db)):
    return await _db_servicess.db_get_form(form_id, user, db)

@app.delete("/forms/delete/{form_id}", status_code=204)
async def db_delete_form(form_id: str, user: _schemas.User=_fastapi.Depends(_auth.get_current_user), db:_orm.Session=_fastapi.Depends(get_db)):
    await _db_servicess.db_delete_form(form_id, user, db)

@app.put("/form/update/{form_id}", status_code=204)
async def db_update_form(form_id: str, form: _schemas.FormCreate, user: _schemas.User=_fastapi.Depends(_auth.get_current_user), db:_orm.Session=_fastapi.Depends(get_db)):
    await _db_servicess.db_update_form(form_id, form, user, db)



if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)