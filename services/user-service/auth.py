from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

# We use bcrypt for secure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Must match the shared secret in jwt_utils.py!
SECRET_KEY = "my_super_secret_jwt_key_for_microservices"
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
   
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
