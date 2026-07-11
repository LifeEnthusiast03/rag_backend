from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, ForeignKey, JSON,Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Users(Base):
    __tablename__ = "Users"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    email = Column(String)
    password = Column(String)
    chats = relationship("Chat", back_populates="user")

class Chat(Base):
    __tablename__ = "Chat"
    chat_id = Column(Integer, primary_key=True, index=True)
    chat_name = Column(String)
    chat_fileloc = Column(String)
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    user = relationship("Users", back_populates="chats")
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    """
    Stores all chat messages (both user and assistant).

    For user messages:
      - role    = "user"
      - content = the question text
      - key_points, sources_cited, follow_up_suggestions are NULL

    For AI assistant messages:
      - role                  = "assistant"
      - content               = the main answer text
      - key_points            = list of key bullet points  (JSON array)
      - sources_cited         = list of citation strings   (JSON array)
      - follow_up_suggestions = list of follow-up questions (JSON array)
    """
    __tablename__ = "Message"
    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("Chat.chat_id"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)

    # Only populated for role="assistant" messages
    key_points = Column(JSON, nullable=True)
    sources_cited = Column(JSON, nullable=True)
    follow_up_suggestions = Column(JSON, nullable=True)

    chat = relationship("Chat", back_populates="messages")

class DocumentChunk(Base):
    __tablename__ = "document_chunk"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("Chat.chat_id"), nullable=False)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSON, nullable=True)   # e.g. {"source": "file.pdf", "page": 3}
    embedding = Column(Vector(768))  # 768 = all-mpnet-base-v2 dimension
    chat = relationship("Chat")