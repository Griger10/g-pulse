from datetime import datetime, timezone, timedelta
from http import HTTPStatus
from typing import override

import jwt
from django.http import HttpResponse
from dmr import Controller, Body, validate, ResponseSpec
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security.jwt import JWTAsyncAuth
from dmr.security.jwt.views import (
    ObtainTokensAsyncController,
    ObtainTokensPayload,
    ObtainTokensResponse,
)

from apps.accounts.api.schemas import (
    UserLogin,
    UserResponse,
    UserCreate,
    UserRefresh,
    AuthenticatedHttpRequest,
    UserUpdate,
    MeResponse,
    AccessTokenResponse,
)
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
                id=str(user.id),
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
            username=payload["username"],
            password=payload["password"],
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


class RefreshController(Controller[PydanticSerializer]):

    @validate(
        ResponseSpec(
            AccessTokenResponse,
            status_code=HTTPStatus.OK,
        ),
        ResponseSpec(dict, status_code=HTTPStatus.UNAUTHORIZED),
    )
    async def post(self, parsed_body: Body[UserRefresh]) -> HttpResponse:
        try:
            payload = jwt.decode(
                parsed_body.refresh_token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return self.to_response(
                {"error": "Refresh token expired"},
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return self.to_response(
                {"error": "Invalid refresh token"},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        extras = payload.get("extras", {})
        if extras.get("type") != "refresh":
            return self.to_response(
                {"error": "Not a refresh token"},
                status_code=HTTPStatus.UNAUTHORIZED,
            )

        now = datetime.now(timezone.utc)
        access_token = jwt.encode(
            {
                "sub": payload["sub"],
                "exp": now
                + timedelta(
                    minutes=settings.JWT_ACCESS_TOKEN_LIFETIME_MINUTES,
                ),
                "token_type": "access",
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        return self.to_response(
            AccessTokenResponse(access_token=access_token),
            status_code=HTTPStatus.OK,
        )


class MeController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            MeResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self) -> HttpResponse:
        db_user = await User.objects.aget(id=self.request.user.id)
        return self.to_response(
            MeResponse(
                id=str(self.request.user.id),
                username=self.request.user.username,
                email=self.request.user.email,
                webhook_url=db_user.webhook_url,
                telegram_chat_id=db_user.telegram_chat_id,
            )
        )

    @validate(
        ResponseSpec(
            MeResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def patch(self, parsed_body: Body[UserUpdate]) -> HttpResponse:
        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        if update_data:
            await User.objects.filter(id=self.request.user.id).aupdate(**update_data)

        user = await User.objects.aget(id=self.request.user.id)
        return self.to_response(
            MeResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                telegram_chat_id=user.telegram_chat_id,
                webhook_url=user.webhook_url,
            )
        )
