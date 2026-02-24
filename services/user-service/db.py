from sqlmodel import create_engine, Session


engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False} )

def get_session():
    with Session(engine) as session:
        yield session