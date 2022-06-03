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