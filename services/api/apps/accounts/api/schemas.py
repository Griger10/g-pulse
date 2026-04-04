from typing import TypedDict

import msgspec
from django.http import HttpRequest
from pydantic import BaseModel, EmailStr, SecretStr

from apps.accounts.models import User


class UserCreate(BaseModel):
    email: EmailStr
    username: str | None = None
    password: SecretStr


class UserResponse(BaseModel):
    uid: str
    username: str
    email: EmailStr


class UserLogin(TypedDict):
    username: str
    password: str


class UserRefresh(BaseModel):
    token: str


class UserInfoRequest(msgspec.Struct):
    uid: str


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    telegram_chat_id: int | None = None
    webhook_url: str | None = None


class MeResponse(BaseModel):
    uid: str
    username: str
    email: EmailStr
    telegram_chat_id: int | None
    webhook_url: str | None
