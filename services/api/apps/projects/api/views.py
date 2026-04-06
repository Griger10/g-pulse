from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, validate, ResponseSpec, Body, Path
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security.jwt import JWTAsyncAuth
from slugify import slugify

from apps.accounts.api.schemas import AuthenticatedHttpRequest
from apps.projects.api.schemas import (
    ProjectInfo,
    ProjectInfoCreate,
    ServiceInfo,
    ProjectSlugPath,
    ServiceInfoCreate,
    ServiceIdPath,
    ProjectInfoUpdate,
    ServiceInfoUpdate,
)
from apps.projects.models import Project, Service


class ProjectsController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            list[ProjectInfo],
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self) -> HttpResponse:
        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(project.owner.id),
                name=project.name,
                slug=project.slug,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            async for project in Project.objects.filter(owner=self.request.user)
        )

    @validate(
        ResponseSpec(
            ProjectInfo,
            status_code=HTTPStatus.CREATED,
        )
    )
    async def post(self, parsed_body: Body[ProjectInfoCreate]) -> HttpResponse:
        slug = slugify(parsed_body.name)
        project = await Project.objects.acreate(
            name=parsed_body.name,
            slug=slug,
            description=parsed_body.description,
            owner=self.request.user,
        )

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(project.owner.id),
                name=project.name,
                slug=project.slug,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )


class ProjectDetailsController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ProjectInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ProjectSlugPath]) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(project.owner.id),
                name=project.name,
                slug=project.slug,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    @validate(
        ResponseSpec(
            ProjectInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def patch(
        self,
        parsed_path: Path[ProjectSlugPath],
        parsed_body: Body[ProjectInfoUpdate],
    ) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )
        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        if update_data:
            await Project.objects.filter(
                id=project.id, owner=self.request.user
            ).aupdate(**update_data)
            project = await Project.objects.aget(id=project.id)

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(project.owner.id),
                name=project.name,
                slug=project.slug,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    @validate(
        ResponseSpec(
            dict,
            status_code=HTTPStatus.NO_CONTENT,
        )
    )
    async def delete(self, parsed_path: Path[ProjectSlugPath]) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )
        await project.adelete()
        return self.to_response({"message": "Successfully deleted project"})


class ServiceController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            list[ServiceInfo],
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ProjectSlugPath]) -> HttpResponse:
        services = Service.objects.filter(
            project__slug=parsed_path["slug"],
            project__owner=self.request.user,
        )

        return self.to_response(
            [
                ServiceInfo(
                    id=str(service.id),
                    name=service.name,
                    url=service.url,
                    check_interval=service.check_interval,
                    expected_status_code=service.expected_status_code,
                    current_status=service.current_status,
                    timeout=service.timeout,
                    is_active=service.is_active,
                    service_type=service.service_type,
                    created_at=service.created_at,
                    updated_at=service.updated_at,
                )
                async for service in services
            ]
        )

    @validate(
        ResponseSpec(
            ServiceInfo,
            status_code=HTTPStatus.CREATED,
        )
    )
    async def post(
        self, parsed_path: Path[ProjectSlugPath], parsed_body: Body[ServiceInfoCreate]
    ):
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )

        service = await Service.objects.acreate(
            name=parsed_body.name,
            url=parsed_body.url,
            check_interval=parsed_body.check_interval,
            expected_status_code=parsed_body.expected_status_code,
            timeout=parsed_body.timeout,
            is_active=parsed_body.is_active,
            service_type=parsed_body.service_type,
            project=project,
        )

        return self.to_response(
            ServiceInfo(
                id=str(service.id),
                name=service.name,
                url=service.url,
                check_interval=service.check_interval,
                expected_status_code=service.expected_status_code,
                current_status=service.current_status,
                timeout=service.timeout,
                is_active=service.is_active,
                service_type=service.service_type,
                created_at=service.created_at,
                updated_at=service.updated_at,
            )
        )


class ServiceDetailsController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ServiceInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ServiceIdPath]):
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        return self.to_response(
            ServiceInfo(
                id=str(service.id),
                name=service.name,
                url=service.url,
                check_interval=service.check_interval,
                expected_status_code=service.expected_status_code,
                service_type=service.service_type,
                current_status=service.current_status,
                timeout=service.timeout,
                is_active=service.is_active,
                created_at=service.created_at,
                updated_at=service.updated_at,
            )
        )

    @validate(
        ResponseSpec(
            ServiceInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def patch(
        self, parsed_path: Path[ServiceIdPath], parsed_body: Body[ServiceInfoUpdate]
    ):
        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        service = await Service.objects.aget(
            id=parsed_path["id"], project__owner=self.request.user
        )

        if update_data:
            service = await Service.objects.filter(
                id=parsed_path["id"], project__owner=self.request.user
            ).aupdate(**update_data)

        return self.to_response(
            ServiceInfo(
                id=str(service.id),
                name=service.name,
                url=service.url,
                check_interval=service.check_interval,
                expected_status_code=service.expected_status_code,
                service_type=service.service_type,
                current_status=service.current_status,
                timeout=service.timeout,
                is_active=service.is_active,
                created_at=service.created_at,
                updated_at=service.updated_at,
            )
        )

    @validate(
        ResponseSpec(
            dict,
            status_code=HTTPStatus.NO_CONTENT,
        )
    )
    async def delete(self, parsed_path: Path[ServiceIdPath]):
        service = await Service.objects.aget(
            id=parsed_path["id"], project__owner=self.request.user
        )

        await service.adelete()
        return self.to_response({"message": "Successfully deleted service"})
