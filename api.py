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

app = FastAPI(openapi_tags=tags_metadata)

class quiz(BaseModel):
    docTitle: str
    title: str
    descr: str = ""

class mcq(BaseModel):
    formid: str
    title: str
    descr: str = None
    required: bool = True
    point: int = 0
    ans: list
    Type: str = "RADIO"
    options: list
    shuffle: bool = True
    idx: int = 0

class textq(BaseModel):
    formid: str
    title: str
    descr: str = None
    required: bool = True
    point: int = 0
    ans: list = [{}]
    para: bool = True
    idx: int = 0

class testqList(BaseModel):
    questions: List[textq]

@app.post('/quiz')
def create_quiz(data: quiz):
    result = create_form(data.docTitle, data.title, data.descr)
    return result

@app.post('/mcq')
def create_mcq(data: mcq):
    question_setting = create_choiceQuestion(data.formid, data.title, data.descr, data.required, data.point, data.ans, data.Type, data.options, data.shuffle, data.idx)
    return question_setting

@app.post('/tq')
def create_textq(datum: testqList):
    quest = []
    for data in datum['questions']:
        if data.para and len(data.ans[0])>0:
            return {"Error": "Correct answer may only be specified for short-test question. If you want to specifie correct answer, please set para=false"}
        question_setting = create_textQuestion(data.formid, data.title, data.descr, data.required, data.point, data.ans, data.para, data.idx)
        quest.append(question_setting)
    return quest

@app.get('/getform')
def getform(id: str):
    res = get_form(id)
    return res

@app.get('/getresponses')
def getresponses(id: str):
    res = get_responses(id)
    return res

if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=8000)