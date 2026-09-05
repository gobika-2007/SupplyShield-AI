from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from backend.services.auth_service import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(request: SignupRequest):

    if len(request.name.strip()) < 2:
        return {
            "success": False,
            "message": "Please enter your full name."
        }

    if len(request.password) < 6:
        return {
            "success": False,
            "message": "Password must contain at least 6 characters."
        }

    return register_user(
        request.name,
        request.email,
        request.password
    )


@router.post("/login")
def login(request: LoginRequest):

    return login_user(
        request.email,
        request.password
    )