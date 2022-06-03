import pydantic as _pydantic
from typing import List

class quiz(_pydantic.BaseModel):
    docTitle: str
    title: str
    descr: str = ""

class postid(_pydantic.BaseModel):
    id: str

class quest(_pydantic.BaseModel):
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

class questList(_pydantic.BaseModel):
    questions: List[quest]

class genQuiz(_pydantic.BaseModel):
    docTitle: str
    title: str
    descr: str = ""
    questions: List[quest]