from sqlalchemy import Column, String, DateTime, Integer, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    qq = Column(Integer)
    conversation_id = Column(String)
    timestamp = Column(DateTime)
    # 联合主键
    __table_args__ = (
        PrimaryKeyConstraint('qq', 'conversation_id'),
    )
