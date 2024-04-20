# x_filter/auth_router.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from x_filter import Database
from x_filter.data.models.user import User
from x_filter.utils.security import authenticate
from x_filter.utils.security import check_password, generate_tokens, hash_password

router = APIRouter()
db = Database()

class User(BaseModel):
    id: str
    password: str
    x_username: str
@router.post("/api/signup/")
def signup(user: User):
    if db.exists("users", user.id):
        return {"message": "User already exists.", "status_code": 400}

    hashed_password = hash_password(user.password)
    db.insert("users", {"id": user.id, "password": hashed_password, "x_username": user.x_username, "filters": {}})

    access_token, refresh_token = generate_tokens(user.id)

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "user": user
    }
class SigninUser(BaseModel):
    id: str
    password: str

@router.post("/api/signin/")
def signin(user: SigninUser):
    user_data = db.query("users", user.id)
    if not user_data:
        return {"message": "User not found.", "status_code": 404}

    if not check_password(user_data["password"], user.password):
        return {"message": "Invalid password.", "status_code": 401}

    user_data.pop("password")
    user_data["id"] = user_data["id"]

    access_token, refresh_token = generate_tokens(user.id)
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "user": user_data
    }

@router.post("/api/secure-endpoint/")
async def secure_endpoint(user_id: str = Depends(authenticate)):
    user = db.query("users", user_id)

    return {"isAuthenticated": True, "user": user}