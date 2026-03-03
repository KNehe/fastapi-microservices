from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from db import engine, get_session
from sqlmodel import SQLModel, Session, select
from models import User, UserPublic
import grpc
import product_pb2
import product_pb2_grpc


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/users/", response_model=UserPublic)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/")
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}/purchases/{product_id}")
def get_user_purchase(user_id: int, product_id: int):
    # Connect to the Product service via gRPC
    with grpc.insecure_channel("product-service:50051") as channel:
        stub = product_pb2_grpc.ProductServiceStub(channel)

        response = stub.GetProduct(product_pb2.ProductRequest(id=product_id))
    
    return {
        "user_id": user_id,
        "product_details": {
            "id": response.id,
            "name": response.name,
            "price": response.price
        },
        "source": "gRPC"
    }
