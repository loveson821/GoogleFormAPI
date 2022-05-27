import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from main import *

tags_metadata = [
    {
        "name": "",
        "description": ""
    }
]

id = ""
app = FastAPI(openapi_tags=tags_metadata)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class quiz(BaseModel):
    docTitle: str
    title: str
    descr: str = ""

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

class questList(BaseModel):
    questions: List[quest]

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

@app.post('/addquestions')
def appquest(data: questList):
    global id
    for q in data.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            question_setting = create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            question_setting = create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    return "done"

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

    return {"id": id, "link": result["responderUri"]}


if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)