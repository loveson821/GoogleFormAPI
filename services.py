from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import os

SCOPES = ["https://www.googleapis.com/auth/forms.body ", "https://www.googleapis.com/auth/drive"]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage('token.json')
if not os.path.exists('token.json'):
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store)
else:
    creds = store.get()

form_service = discovery.build('forms', 'v1', http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# https://developers.google.com/forms/api/reference/rest/v1/forms
def create_form(docTitle="",title="",descr=""):
    FORM = {
        "info": {
            "documentTitle": docTitle,
            "title": title
        }
    }
    setting = {
        "requests": [
            {
                "updateSettings": {
                    "settings": {
                        "quizSettings": {
                            "isQuiz": True
                        }
                    },
                    "updateMask": "quizSettings.isQuiz"
                }
            }
        ]
    }
    
    des = {
        "requests": [
            {
                "updateFormInfo": {
                    "info": {
                        "description": descr
                    },
                    "updateMask": "description"
                }
            }
        ]
    }
    result = form_service.forms().create(body=FORM).execute()

    id = result['formId']
    form_service.forms().batchUpdate(formId=id, body=setting).execute()
    form_service.forms().batchUpdate(formId=id, body=des).execute()

    return result

def create_choiceQuestion(id,question="",descr="",required=True,point=0,ans=[{"value": ""}],Type="RADIO",options=[{"value": ""}],shuffle=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem": {
                "item": {
                    "title": question,
                    "description": descr,
                    "questionItem": {
                        "question": {
                            "required": required,    
                            "grading": {
                                "pointValue": point,
                                "correctAnswers": {
                                    "answers": ans
                                }
                            },
                            "choiceQuestion": {
                                "type": Type,
                                "options": options,
                                "shuffle": shuffle
                            }
                        }
                    }
                },
                "location": {
                    "index": idx
                }
            }
        }]
    }

    question_setting = form_service.forms().batchUpdate(formId=id, body=QUESTION).execute()
    return question_setting

def create_textQuestion(id,question="",descr="",required=True,point=0,ans=[{}],para=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem": {
                "item": {
                    "title": question,
                    "description": descr,
                    "questionItem": {
                        "question": {
                            "required": required,    
                            "grading": {
                                "pointValue": point,
                                # "correctAnswers": {
                                #     "answers": ans if not para else [{}]
                                # }
                            },
                            "textQuestion": {
                                "paragraph": para
                            }
                        }
                    }
                },
                "location": {
                    "index": idx
                }
            }
        }]
    }

    if not para:
        QUESTION['requests'][0]["createItem"]['item']['questionItem']['question']['grading']["correctAnswers"]={"answers": ans }

    question_setting = form_service.forms().batchUpdate(formId=id, body=QUESTION).execute()
    return question_setting

def get_form(id):
    get_result = form_service.forms().get(formId=id).execute()
    return get_result
    
def get_responses(id):
    form = get_form(id)
    quest = {}
    items = form['items']
    for item in items:
        qid = item['questionItem']['question']['questionId']
        quest[qid] = {'title': item['title'], 'correctAnswer': item['questionItem']['question']['grading']['correctAnswers']}

    res = form_service.forms().responses().list(formId=id).execute()
    if 'responses' not in res:
        return res

    ress = []

    for r in res['responses']:
        tmp = {
            "responseId": r['responseId'],
            "questions": []
        }
        for q in quest:
            if q not in r['answers']:
                continue
            tmp['questions'].append({quest[q]['title'] : {
                    "questionId": q,
                    "answer": r['answers'][q]['textAnswers']['answers'],
                    "correctAnswer": quest[q]['correctAnswer'],
                    "score": r['answers'][q]['grade']['score'] if 'score' in r['answers'][q]['grade'] else 0
                }})
        tmp["totalScore"] = r['totalScore'] if 'totalScore' in r else 0
        ress.append(tmp)

    return ress

def get_link(id):
    link = get_form(id)['responderUri']
    return link



import datetime as _dt
import fastapi as _fastapi
import fastapi.security as _security
import database as _database
import models as _models
import schemas as _schemas
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt

def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset

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

async def _form_selector(id: int, user: _schemas.User, db:_orm.Session):
    form = db.query(_models.form).filter_by(owner_id=user.id).filter(_models.form.id == id).first()

    if form is None:
        raise _fastapi.HTTPException(status_code=401, detail="Form dose not exist")

    return form

async def db_get_form(id: int, user: _schemas.User, db:_orm.Session):
    form = await _form_selector(id, user, db)

    return _schemas.Form.from_orm(form)

async def db_delete_form(id: int, user: _schemas.User, db: _orm.Session):
    form = await _form_selector(id, user, db)

    db.delete(form)
    db.commit()

async def db_update_form(id: int, form: _schemas.FormCreate, user: _schemas.User, db: _orm.Session):
    form_db = await _form_selector(id, user, db)

    form_db.form_id = form.form_id
    form_db.link = form.link
    form_db.title = form.title
    form_db.by = form.by
    form_db.date = form.date
    form_db.date_last_updated = utc2local(_dt.datetime.utcnow())

    db.commit()

    return _schemas.Form.from_orm(form_db)