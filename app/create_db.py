from database import Base,engine
from models.models import *

Base.metadata.create_all(engine)