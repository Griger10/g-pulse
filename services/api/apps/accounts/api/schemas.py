from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str | None = None
    password: SecretStr


class UserResponse(BaseModel):
    uid: str
    username: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str
