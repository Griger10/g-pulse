from django.urls import include

from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, SwaggerView
from dmr.plugins.pydantic import PydanticSerializer
from dmr.routing import Router, build_404_handler, build_500_handler, path

from apps.accounts.api.urls import accounts_router

router = Router(
    prefix="api/v1/",
    urls=[
        path(
            accounts_router.prefix,
            include((accounts_router.urls, "accounts"), namespace="accounts"),
        ),
    ],
)

schema = build_schema(router)

urlpatterns = [
    path(router.prefix, include((router.urls, "config"), namespace="api")),
    path("docs/openapi.json/", OpenAPIJsonView.as_view(schema), name="openapi"),
    path("docs/swagger/", SwaggerView.as_view(schema), name="swagger"),
]


handler404 = build_404_handler(router.prefix, serializer=PydanticSerializer)
handler500 = build_500_handler(router.prefix, serializer=PydanticSerializer)
