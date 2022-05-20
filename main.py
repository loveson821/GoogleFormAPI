from __future__ import print_function

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from pyparsing import restOfLine

id='1cSfuhv4v1soyiMWu9aHNyFitBrlLgiZ51G_WJP5KuMo'
SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage('token.json')
creds = None
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store)

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

    result = form_service.forms().create(body=FORM).execute()
    return result

def create_choiceQuestion(formId,title="",descr="",required=True,point=0,ans=[{"value": ""}],type="RADIO",options=[{"value": ""}],shuffle=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem:": {
                "item": {
                    "title": title,
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
                                "type": type,
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

    question_setting = form_service.forms().batchUpdate(formId=formId, body=QUESTION).execute()
    return question_setting

def create_textQuestion(formId,title="",descr="",required=True,point=0,ans=[{"value": ""}],para=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem:": {
                "item": {
                    "title": title,
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

    question_setting = form_service.forms().batchUpdate(formId=formId, body=QUESTION).execute()
    return question_setting

def get_form(formId):
    get_result = form_service.forms().get(formId=formId).execute()
    print(get_result)
    return get_result
    
def get_responses(formId):
    res = service.forms().responses().list(formId=formId).execute()
    print(res)
    return res