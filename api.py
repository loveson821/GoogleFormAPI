import uvicorn
import models as _models
import fastapi as _fastapi
from fastapi.middleware.cors import CORSMiddleware

import services as _services

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

@app.post('/quiz')
def create_quiz(data: _models.quiz):
    result = _services.create_form(data.docTitle, data.title, data.descr)
    global id
    id = result['formId']
    return result

@app.post('/id')
def post_id(formId: _models.postid):
    global id
    id = formId.id
    return id

@app.post('/addquestions')
def appquest(data: _models.questList):
    global id
    for q in data.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            _services.create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            _services.create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    return "done"

@app.get('/getform')
def getform(id: str):
    res = _services.get_form(id)
    return res

@app.get('/getresponses')
def getresponses(id: str):
    res = _services.get_responses(id)
    return res

@app.post('/generate')
def gen(form: _models.genQuiz):
    result = _services.create_form(form.docTitle, form.title, form.descr)
    global id
    id = result['formId']

    for q in form.questions:
        if not len(q.formid):
            q.formid = id
        if not len(q.Type):
            _services.create_textQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.para, q.idx)
        else:
            _services.create_choiceQuestion(q.formid, q.title, q.descr, q.required, q.point, q.ans, q.Type, q.options, q.shuffle, q.idx)

    return {"id": id, "link": result["responderUri"]}


if __name__ == '__main__':
    uvicorn.run('api:app', host='127.0.0.1', port=5000)