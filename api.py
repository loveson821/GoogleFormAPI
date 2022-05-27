import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from main import *

tags_metadata = [
    {
        "name": "",
        "description": ""
    }
]

id = ""
app = FastAPI(openapi_tags=tags_metadata)

class quiz(BaseModel):
    docTitle: str
    title: str
    descr: str = ""

class mcq(BaseModel):
    formid: str
    title: str
    descr: str = ""
    required: bool = True
    point: int = 0
    ans: list
    Type: str = "RADIO"
    options: list
    shuffle: bool = True
    idx: int = 0

class textq(BaseModel):
    formid: str = ""
    title: str
    descr: str = ""
    required: bool = True
    point: int = 0
    ans: list = [{}]
    para: bool = True
    idx: int = 0

class testqList(BaseModel):
    questions: List[textq]

class postid(BaseModel):
    id: str

class quest(BaseModel):
    formid: str = ""
    title: str
    descr: str = ""
    required: bool = True
    point: int = 0
    ans: list = [{}]
    para: bool = True
    Type: str = ""
    options: list = [{}]
    shuffle: bool = True
    idx: int = 0

class genQuiz(BaseModel):
    docTitle: str
    title: str
    descr: str = ""
    questions: List[quest]


@app.post('/quiz')
def create_quiz(data: quiz):
    result = create_form(data.docTitle, data.title, data.descr)
    global id
    id = result['formId']
    return result

@app.post('/id')
def post_id(formId: postid):
    global id
    id = formId.id
    return id

@app.get('/')
def home():
    return id

# @app.post('/mcq')
# def create_mcq(data: mcq):
#     question_setting = create_choiceQuestion(data.formid, data.title, data.descr, data.required, data.point, data.ans, data.Type, data.options, data.shuffle, data.idx)
#     return question_setting

# @app.post('/tq')
# def create_textq(datum: testqList):
#     global id
#     quest = []
#     for data in datum.questions:
#         if not len(data.formid):
#             data.formid = id
#         if data.para :
#             data.ans = [{}]
#             # return {"Error": "Correct answer may only be specified for short-test question. If you want to specifie correct answer, please set para=false"}
#         question_setting = create_textQuestion(data.formid, data.title, data.descr, data.required, data.point, data.ans, data.para, data.idx)
#         quest.append(question_setting)
#     return quest

@app.get('/getform')
def getform(id: str):
    res = get_form(id)
    return res

@app.get('/getresponses')
def getresponses(id: str):
    res = get_responses(id)
    return res

@app.post('/generate')
def gen(form: genQuiz):
    result = create_form(form.docTitle, form.title, form.descr)
    global id
    id = result['formId']

    for q in form.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            question_setting = create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            question_setting = create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    return result["responderUri"]


if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=8000)