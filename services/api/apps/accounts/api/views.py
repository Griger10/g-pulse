from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from typing import override

from django.http import HttpResponse
from dmr import Controller, Body, validate, ResponseSpec
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security.jwt.views import (
    ObtainTokensAsyncController,
    ObtainTokensPayload,
    ObtainTokensResponse,
)

from apps.accounts.api.schemas import UserLogin, UserResponse, UserCreate
from apps.accounts.models import User
from config import settings


class RegisterController(Controller[PydanticSerializer]):
    @validate(
        ResponseSpec(
            UserResponse,
            status_code=HTTPStatus.CREATED,
        )
    )
    async def post(self, parsed_body: Body[UserCreate]) -> HttpResponse:
        user = await User.objects.acreate_user(
            username=(
                parsed_body.username if parsed_body.username else parsed_body.email
            ),
            email=parsed_body.email,
            password=parsed_body.password.get_secret_value(),
        )
        return self.to_response(
            UserResponse(
                uid=user.id,
                username=parsed_body.username,
                email=parsed_body.email,
            ),
            status_code=HTTPStatus.CREATED,
        )


class LoginController(
    ObtainTokensAsyncController[
        PydanticSerializer,
        UserLogin,
        ObtainTokensResponse,
    ],
):
    @override
    async def convert_auth_payload(
        self,
        payload: UserLogin,
    ) -> ObtainTokensPayload:
        return ObtainTokensPayload(
            username=payload.email,
            password=payload.password,
        )

    @override
    async def make_api_response(self) -> ObtainTokensResponse:
        now = datetime.now(timezone.utc)
        return {
            "access_token": self.create_jwt_token(
                expiration=now
                + timedelta(
                    minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES,
                ),
                token_type="access",
            ),
            "refresh_token": self.create_jwt_token(
                expiration=now
                + timedelta(
                    days=settings.JWT_REFRESH_TOKEN_LIFETIME_DAYS,
                ),
                token_type="refresh",
            ),
        }
