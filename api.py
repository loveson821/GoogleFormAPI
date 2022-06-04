import uvicorn
import schemas as _schemas
import fastapi as _fastapi
from fastapi.middleware.cors import CORSMiddleware
import fastapi.security as _security
from typing import List

import sqlalchemy.orm as _orm
import services as _services
import schemas as _schemas

tags_metadata = [
    {
        "name": "",
        "description": ""
    }
]

id = ""
app = _fastapi.FastAPI(openapi_tags=tags_metadata)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/getform')
def get_form(id: str, user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    res = _services.get_form(id)
    return res

@app.get('/getresponses')
def get_responses(id: str, user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    res = _services.get_responses(id)
    return res

@app.post('/generate')
async def gen(form: _schemas.genQuiz, user: _schemas.User = _fastapi.Depends(_services.get_current_user), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    result = _services.create_form(form.docTitle, form.title, form.descr)
    id = result['formId']

    for q in form.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            _services.create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            _services.create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    form_create = _schemas.FormCreate(form_id=result['formId'], link=result["responderUri"],title=form.title,by=form.by,date=form.date)
    await _services.db_create_form(user, db, form_create)
    return {"id": id, "link": result["responderUri"]}

@app.post("/user/create")
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_username(user.username, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Username already exists")
    
    user_obj = await _services.create_user(user, db)

    return await _services.create_token(user_obj)

@app.post("/user/token")
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user)

@app.get("/user/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user

@app.put("/user/update")
async def update_user(username: str, password: str, new_username: str="", new_password: str="", user: _schemas.User = _fastapi.Depends(_services.get_current_user), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    await _services.update_user(user, username, password, new_username, new_password, db)
    return {"message": "Successfully Updated"}

@app.delete("/user/delete")
async def delete_user(username: str, password: str, user: _schemas.User = _fastapi.Depends(_services.get_current_user), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    await _services.delete_user(user, username, password, db)
    return {"message": "Successfully Deleted"}

@app.post("/fomrs", response_model=_schemas.Form)
async def db_create_form(form: _schemas.FormCreate, user: _schemas.User=_fastapi.Depends(_services.get_current_user), db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.create_lead(user, db, form)

@app.get("/forms", response_model=List[_schemas.Form])
async def db_get_forms(user: _schemas.User=_fastapi.Depends(_services.get_current_user), db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.db_get_forms(user, db)

@app.get("/fomrs/{id}", status_code=200)
async def db_get_form(id: int, user: _schemas.User=_fastapi.Depends(_services.get_current_user), db:_orm.Session=_fastapi.Depends(_services.get_db)):
    return await _services.db_get_form(id, user, db)

@app.delete("/forms/delete/{id}", status_code=204)
async def db_delete_form(id: int, user: _schemas.User=_fastapi.Depends(_services.get_current_user), db:_orm.Session=_fastapi.Depends(_services.get_db)):
    await _services.db_delete_form(id, user, db)
    return {"message": "Successfully Deleted"}

@app.put("/form/update/{id}", status_code=204)
async def db_update_form(id: int, form: _schemas.FormCreate, user: _schemas.User=_fastapi.Depends(_services.get_current_user), db:_orm.Session=_fastapi.Depends(_services.get_db)):
    await _services.db_update_form(id, form, user, db)
    return {"message", "Successfully Updated"}



if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)