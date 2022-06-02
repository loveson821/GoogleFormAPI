from pydantic import BaseModel
from typing import List

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