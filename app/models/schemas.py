import datetime
from typing import List, Optional

from pydantic import BaseModel


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
    text: str = ""
    by: str
    date: str
    questions: List[quest]

# Users Authorization


class _UserBase(BaseModel):
    username: str


class UserCreate(_UserBase):
    password: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    password: str
    new_password: str = ""
    new_username: str = ""

# Form


class _FormBase(BaseModel):
    form_id: str
    link: str
    title: str
    by: str
    date: str
    text: Optional[str]
    deleted: bool = False


class FormCreate(_FormBase):
    pass


class Form(_FormBase):
    id: int
    owner_id: int
    date_created: datetime.datetime
    date_last_updated: datetime.datetime

    class Config:
        orm_mode = True

# Summarize


class summarize_text(BaseModel):
    text: str
    percent: float
