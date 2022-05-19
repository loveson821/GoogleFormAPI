from __future__ import print_function

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from pyparsing import restOfLine

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

def create_choiceQuestion(result,title="",descr="",required=True,type="RADIO",options=[{"value": ""}],shuffle=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem:": {
                "item": {
                    "title": title,
                    "description": descr,
                    "questionItem": {
                        "question": {
                            "required": required,
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

    question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=QUESTION).execute()
    return question_setting

def create_textQuestion(result,title="",descr="",required=True,para=True,idx=0):
    QUESTION = {
        "requests": [{
            "createItem:": {
                "item": {
                    "title": title,
                    "description": descr,
                    "questionItem": {
                        "question": {
                            "required": required,
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

    question_setting = form_service.forms().batchUpdate(formId=result["formId"], body=QUESTION).execute()
    return question_setting

def get_form(result):
    get_result = form_service.forms().get(formId=result["formId"]).execute()
    print(get_result)
    return get_result
    