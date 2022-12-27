import os
import pathlib
import uuid
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .conversation import Conversation
from .user import User

# 获取用户的主目录
home_dir = pathlib.Path.home()
# 将数据库文件保存在用户的主目录的 .lopop 目录下
database_path = os.path.join(home_dir, '.lopop', 'chatgpt', 'database.db')
# 创建 .lopop 目录，如果它不存在
os.makedirs(os.path.dirname(database_path), exist_ok=True)
# 创建数据库引擎
engine = create_engine(f'sqlite:///{database_path}')
# 创建基类
Base = declarative_base()
# 使用基类创建类对应的表
Base.metadata.create_all(bind=engine, tables=[User.__table__, Conversation.__table__])

Session = sessionmaker(bind=engine)


class qaDao():

    def save_conversation(self, coversation: Conversation):
        """保存问题和答案到数据库中"""
        session = Session()
        session.add(coversation)
        session.commit()

    def query(self, conversation_id: int, limit_num=5) -> List[str]:
        """查询会话的所有消息"""
        session = Session()
        # 查询会话的所有消息
        conversation_list = session.query(Conversation) \
            .filter(Conversation.conversation_id == conversation_id) \
            .order_by(Conversation.timestamp.asc()) \
            .limit(limit_num).all()

        # 将会话信息转换为字符串列表
        conversation_str_list = [f"{conversation.question}: {conversation.answer}" for conversation in
                                 conversation_list]

        # 返回会话字符串列表
        return conversation_str_list

    def __save_conversation_id(self, user: User):  # __开头表示私有
        """保存用户最新的会话ID"""
        session = Session()
        session.add(user)
        session.commit()

    def regenerate_conversation_id(self, qq):
        """清空历史，重新生成会话ID"""
        conversation_id = str(uuid.uuid4())
        self.__save_conversation_id(User(qq=qq, conversation_id=conversation_id))
        return conversation_id

    def get_latest_conversation_id(self, qq):
        """获取用户最新的会话ID"""
        session = Session()
        # 查询 users 表中 user_id 为 qq 的最新一条数据
        latest_conversation = (
            session.query(User)
            .filter(User.qq == qq)
            .order_by(User.timestamp.desc())
            .first()
        )
        # 如果查询到了最新的一条数据，返回 conversation_id
        if latest_conversation:
            return latest_conversation.conversation_id
        # 如果没有查询到最新的一条数据，重新生成一个
        return self.regenerate_conversation_id(qq)

    # 不使用update了，效率低
    def update_conversation(self, cvs: Conversation):
        session = Session()
        conversation = session.query(Conversation).filter(Conversation.conversation_id == cvs.conversation_id) \
            .order_by(Conversation.timestamp.desc()).first()
        # 修改记录
        conversation.question = cvs.question
        conversation.answer = cvs.answer
        conversation.timestamp = cvs.timestamp
        session.commit()

    def get_context(self, conversation_id):
        """获取最近的上下文"""
        session = Session()
        conversation = session.query(Conversation).filter(Conversation.conversation_id == conversation_id) \
            .order_by(Conversation.timestamp.desc()).first()
        if conversation:
            return conversation.answer
        else:
            return ''
