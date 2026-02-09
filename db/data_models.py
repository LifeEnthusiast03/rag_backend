from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer,String,Column,ForeignKey
from sqlalchemy.orm import relationship
Base = declarative_base()

class Users(Base):
    __tablename__="Users"
    user_id = Column(Integer,primary_key=True,index=True)
    user_name=Column(String)
    email=Column(String)
    password = Column(String)
    chats = relationship("Chat",back_populates="user")
class Chat(Base):
    __tablename__="Chat"
    chat_id=Column(Integer,primary_key=True,index=True)
    chat_name=Column(String)
    user_id = Column(Integer,ForeignKey("Users.user_id"))
    user = relationship("Users",back_populates="chats")
    messages = relationship("Message",back_populates="chat")

class Message(Base):
    __tablename__="Message"
    message_id = Column(Integer,primary_key=True,index=True)
    chat_id = Column(Integer,ForeignKey("Chat.chat_id"))
    role = Column(String)
    content = Column(String)
    chat = relationship("Chat",back_populates="messages")