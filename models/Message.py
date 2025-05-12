from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from database import engine, Base, Session
from contextlib import contextmanager
import time

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forwarded_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=time.strftime("%Y-%m-%d %H:%M:%S"))

    def __init__(self, message: str, forwarded_id: int = None, created_at: str = None):
        if created_at is None:
            created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.message = message
        self.created_at = created_at
        self.forwarded_id = forwarded_id

    
    @classmethod
    def create(cls, message: str, forwarded_id: int = None):
        with session_scope() as session:
            new_message = cls(message=message, forwarded_id=forwarded_id)
            session.add(new_message)
            session.commit()
            return new_message
        
    @classmethod
    def get_all(cls):
        with session_scope() as session:
            return session.query(cls).all()
        
    @classmethod
    def get(cls, forwarded_id: int):
        with session_scope() as session:
            return session.query(cls).filter(cls.forwarded_id == forwarded_id).first()
        
    @classmethod
    def delete(cls, forwarded_id: int):
        with session_scope() as session:
            message = session.query(cls).filter(cls.forwarded_id == forwarded_id).first()
            if message:
                session.delete(message)
                session.commit()
                return True
            return False
        
    @classmethod
    def update(cls, forwarded_id: int, message: str):
        with session_scope() as session:
            msg = session.query(cls).filter(cls.forwarded_id == forwarded_id).first()
            if msg:
                msg.message = message
                session.commit()
                return msg
            return None

    def __repr__(self):
        return f"<Message(id={self.id}, message={self.message}, created_at={self.created_at})>"