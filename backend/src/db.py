from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import text

URL_DATABASE = 'mysql+pymysql://root@localhost:3306/test'

engine = create_engine(URL_DATABASE)
session = Session(engine)

session.execute(text("select * from information_schema.tables"))

'''
    considering just leaving db in memory for this prototype
'''
