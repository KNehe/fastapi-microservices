from fastapi import FastAPI, Depends, HTTPException, Response, status
from contextlib import asynccontextmanager
from db import engine, get_session
from sqlmodel import SQLModel, Session, select, text
from models import User, UserPublic
import grpc
import product_pb2
import product_pb2_grpc
from fastapi.middleware.cors import CORSMiddleware
from auth import hash_password, verify_password, create_access_token
from shared.jwt_utils import verify_token
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

# 1. Name the service so we can identify it in the background
resource = Resource.create({"service.name": "user-service"})
provider = TracerProvider(resource=resource)

# 2. Tell it where to send the traces (our Jaeger container)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# 3. Auto-instrument the FastAPI app
FastAPIInstrumentor.instrument_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/", response_model=UserPublic)
def create_user(user: User, session: Session = Depends(get_session)):
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/")
def read_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}/purchases/{product_id}")
def get_user_purchase(
    user_id: int, 
    product_id: int,
    token_data: dict = Depends(verify_token)
    ):
    print(f"HOLA")
    raise HTTPException(status_code=403, detail="Not authorized to access this resource")

    if str(user_id) != token_data.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")

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


@app.post("/login")
def login(user_data: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_data.email)
    db_user = session.exec(statement).first()
   
    if not db_user or not verify_password(user_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
   
    token = create_access_token(data={"sub": str(db_user.id), "email": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/health/liveness", tags=["Health"])
def liveness_probe():
    """Checks if the FastAPI server is running."""
    return {"status": "alive"}

@app.get("/health/readiness", tags=["Health"])
def readiness_probe(response: Response, session: Session = Depends(get_session)):
    """Checks if the service is ready to handle traffic (e.g., DB connected)."""
    try:
        # Execute a simple ping to the database
        session.exec(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        # If the DB is unreachable, return a 503 error
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "detail": str(e)}