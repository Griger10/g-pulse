from django.urls import include, path

from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, SwaggerView
from dmr.routing import Router


router = Router(prefix="api/", urls=[])

schema = build_schema(router)

urlpatterns = [
    path(router.prefix, include((router.urls, "your_app"), namespace="api")),
    path("docs/openapi.json/", OpenAPIJsonView.as_view(schema), name="openapi"),
    path("docs/swagger/", SwaggerView.as_view(schema), name="swagger"),
]
