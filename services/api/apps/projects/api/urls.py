from dmr.routing import Router, path

from apps.projects.api.views import (
    ProjectsController,
    ProjectDetailsController,
    ServiceController,
    ServiceDetailsController,
    ServiceCheckController,
)

projects_router = Router(
    prefix="projects/",
    urls=[
        path("", ProjectsController.as_view(), name="projects"),
        path(
            "<slug:slug>/",
            ProjectDetailsController.as_view(),
            name="project_details",
        ),
        path(
            "<slug:slug>/services/",
            ServiceController.as_view(),
            name="project_services",
        ),
    ],
)

service_router = Router(
    prefix="services/",
    urls=[
        path(
            "<uuid:id>/",
            ServiceDetailsController.as_view(),
            name="service_details",
        ),
        path(
            "<uuid:id>/check/",
            ServiceCheckController.as_view(),
            name="service_check",
        ),
    ],
)
