from __future__ import print_function

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from pyparsing import restOfLine

SCOPES = ["https://www.googleapis.com/auth/forms.body ", "https://www.googleapis.com/auth/drive"]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage('token.json')
creds = store.get()
# creds = None
# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
#     creds = tools.run_flow(flow, store)

form_service = discovery.build('forms', 'v1', http=creds.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# https://developers.google.com/forms/api/reference/rest/v1/forms
def create_form(docTitle="",title="",descr=""):
    FORM = {
        "info": {
            "documentTitle": docTitle,
            "title": title,
            "description": descr,
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
    result = form_service.forms().create(body=FORM).execute()
    id = result['formId']
    form_service.forms().batchUpdate(formId=id, body=setting).execute()
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

def create_textQuestion(id,question="",descr="",required=True,point=0,ans=[{"value": ""}],para=True,idx=0):
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

    question_setting = form_service.forms().batchUpdate(formId=id, body=QUESTION).execute()
    return question_setting

def get_form(id):
    get_result = form_service.forms().get(formId=id).execute()
    return get_result
    
def get_responses(id):
    form = get_form(id)
    quest_id = {}
    items = form['items']
    for item in items:
        qid = item['questionItem']['question']['questionId']
        question = item['title']
        quest_id[qid] = question
    res = form_service.forms().responses().list(formId=id).execute()

    return res

def get_link(id):
    link = get_form(id)['responderUri']
    return link