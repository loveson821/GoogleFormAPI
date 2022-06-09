import os

import sqlalchemy as sa
import sqlalchemy.orm as orm
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
#engine = sa.create_engine(DATABASE_URL, pool_size=5,
#                         max_overflow=2, timeout=30)
engine = sa.create_engine(DATABASE_URL)
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
