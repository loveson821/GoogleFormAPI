import datetime as _dt
import pydantic as _pydantic
from typing import List, Optional

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
    by: str
    date: str
    questions: List[quest]

# Users Authorization
class _UserBase(_pydantic.BaseModel):
    username: str

class UserCreate(_UserBase):
    password: str

    class Config:
        orm_mode = True

class User(_UserBase):
    id: int

    class Config:
        orm_mode = True

# Form
class _FormBase(_pydantic.BaseModel):
    form_id: str
    link: str
    title: str
    by: str
    date: str
    text: Optional[str]
    deleted: bool=False

class FormCreate(_FormBase):
    pass

class Form(_FormBase):
    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        orm_mode = True
