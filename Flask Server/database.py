from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
import os

Base = declarative_base()

class Dataset(Base):
    __tablename__ = 'datasets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    file_count = Column(Integer, default=0)
    collection_name = Column(String(255), unique=True, nullable=False)

class ChorusModel(Base):
    __tablename__ = 'chorus_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    responder_llms = Column(JSON)  # List of LLMs that generate responses
    evaluator_llms = Column(JSON)  # List of LLMs that vote on responses
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

class Bot(Base):
    __tablename__ = 'bots'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    instructions = Column(Text, nullable=False)
    dataset_id = Column(Integer)
    chorus_model_id = Column(Integer)
    rag_results_count = Column(Integer, default=5)  # Number of context chunks to retrieve
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    chunks_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

# Database setup
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'chorus.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'chorus.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    print(f"Database initialized at {db_path}")

