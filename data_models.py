from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer,String,Column
Base = declarative_base()

class users(Base):
    __tablename__="users"
    user_id = Column(Integer,primary_key=True,index=True)
    user_name=Column(String)
    Password = Column(String)
class chat(Base):
    __tablename__="chat"
    chat_id=Column(Integer,primary_key=True,index=True)
    chat_name=Column(String)