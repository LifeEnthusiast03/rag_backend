from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer,String,Column
Base = declarative_base()

class Users(Base):
    __tablename__="Users"
    user_id = Column(Integer,primary_key=True,index=True)
    user_name=Column(String)
    email=Column(String)
    password = Column(String)
class Chat(Base):
    __tablename__="Chat"
    chat_id=Column(Integer,primary_key=True,index=True)
    chat_name=Column(String)