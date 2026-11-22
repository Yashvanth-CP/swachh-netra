from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from app.core.database import users_col
from app.core.security import hash_password, verify_password, create_token
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None
    password: str = Field(min_length=6)

@router.post("/register")
def register(data: RegisterRequest):
    email = data.email.lower().strip()
    if users_col.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
        "name": data.name,
        "email": email,
        "phone": data.phone,
        "password_hash": hash_password(data.password),
        "role": "citizen",          # everyone starts as citizen
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    users_col.insert_one(user)
    return {"id": str(user["_id"]), "name": user["name"],
            "email": email, "role": "citizen"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = users_col.find_one({"email": form.username.lower().strip()})
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    token = create_token(str(user["_id"]), user["role"])
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": str(user["_id"]), "name": user["name"],
            "email": user["email"], "role": user["role"]}