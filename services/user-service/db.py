from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}


engine = create_engine(DATABASE_URL,  connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session