from fastapi import FastAPI
from pydantic import BaseModel

from main import *

app = FastAPI()

class quiz(BaseModel):
    docTitle: str
    title: str
    descr: str = None

class mcq(BaseModel):
    formid: str
    title: str
    descr: str = None
    required: bool = True
    point: int = 0
    ans: list = [{"value":""}]
    Type: str = "RADIO"
    options: list = [{"value":""}]
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

@app.get('/')
def home():
    return {"data": "test"}

@app.post('/quiz')
def create_quiz(data: quiz):
    result = create_form(data.docTitle, data.title, data.descr)
    return result

@app.post('/mcq')
def create_mcq(data: mcq):
    return data

@app.post('/tq')
def create_textq(data: textq):
    question_setting = create_textQuestion(data.formid, data.title, data.descr, data.required, data.point, data.ans, data.para, data.idx)
    return question_setting

@app.get('/getform')
def getform(id: str):
    res = get_form(id)
    return res

@app.get('/getresponses')
def getresponses(id: str):
    res = get_responses(id)
    return res