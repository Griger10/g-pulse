from dmr.routing import Router, path

from apps.accounts.api.views import (
    RegisterController,
    LoginController,
    RefreshController,
    MeController,
)

accounts_router = Router(
    "accounts/",
    [
        path("register/", RegisterController.as_view(), name="register"),
        path("login/", LoginController.as_view(), name="login"),
        path("refresh/", RefreshController.as_view(), name="refresh"),
        path("me/", MeController.as_view(), name="me"),
    ],
)
