from dmr.routing import Router, path

from apps.monitoring.api.views import (
    HealthChecksController,
    UptimeController,
    ProjectStatusController,
)

monitoring_router = Router(
    prefix="services/",
    urls=[
        path(
            "<uuid:id>/checks/",
            HealthChecksController.as_view(),
            name="health_checks",
        ),
        path(
            "<uuid:id>/uptime/",
            UptimeController.as_view(),
            name="uptime",
        ),
    ],
)

status_router = Router(
    prefix="projects/",
    urls=[
        path(
            "<slug:slug>/status/",
            ProjectStatusController.as_view(),
            name="project_status",
        ),
    ],
)
