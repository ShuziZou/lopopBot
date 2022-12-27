from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String)
    question = Column(String)
    answer = Column(String)
    timestamp = Column(DateTime)
