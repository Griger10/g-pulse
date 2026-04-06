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
    id: str
    username: str
    email: EmailStr


class UserLogin(TypedDict):
    username: str
    password: str


class UserRefresh(BaseModel):
    refresh_token: str


class AuthenticatedHttpRequest(HttpRequest):
    user: User


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    telegram_chat_id: int | None = None
    webhook_url: str | None = None


class MeResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    telegram_chat_id: int | None
    webhook_url: str | None


class AccessTokenResponse(BaseModel):
    access_token: str
