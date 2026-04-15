from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, validate, ResponseSpec, Body, Path, modify
from dmr.plugins.pydantic import PydanticFastSerializer
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
    ServiceCheckResponse,
)
from apps.projects.models import Project, Service


class ProjectsController(Controller[PydanticFastSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            list[ProjectInfo],
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self) -> HttpResponse:
        user = await self.request.auser()
        projects = []
        async for project in Project.objects.filter(owner=user):
            projects.append(
                ProjectInfo(
                    id=str(project.id),
                    owner_id=str(user.id),
                    name=project.name,
                    slug=project.slug,
                    description=project.description,
                    created_at=project.created_at,
                    updated_at=project.updated_at,
                )
            )
        return self.to_response(projects)

    @validate(
        ResponseSpec(
            ProjectInfo,
            status_code=HTTPStatus.CREATED,
        )
    )
    async def post(self, parsed_body: Body[ProjectInfoCreate]) -> HttpResponse:
        slug = slugify(parsed_body.name)
        user = await self.request.auser()
        project = await Project.objects.acreate(
            name=parsed_body.name,
            slug=slug,
            description=parsed_body.description,
            owner=user,
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


class ProjectDetailsController(Controller[PydanticFastSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ProjectInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ProjectSlugPath]) -> HttpResponse:
        user = await self.request.auser()
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=user,
        )

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(user.id),
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
        user = await self.request.auser()
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=user,
        )
        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        if update_data:
            await Project.objects.filter(id=project.id, owner=user).aupdate(
                **update_data
            )
            project = await Project.objects.aget(id=project.id)

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
                owner_id=str(user.id),
                name=project.name,
                slug=project.slug,
                description=project.description,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
        )

    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def delete(self, parsed_path: Path[ProjectSlugPath]) -> None:
        user = await self.request.auser()
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=user,
        )
        await project.adelete()
        return None


class ServiceController(Controller[PydanticFastSerializer]):
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
    ) -> HttpResponse:
        user = await self.request.auser()
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=user,
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


class ServiceDetailsController(Controller[PydanticFastSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ServiceInfo,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ServiceIdPath]) -> HttpResponse:
        user = await self.request.auser()
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=user,
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
    ) -> HttpResponse:
        user = await self.request.auser()
        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        service = await Service.objects.aget(id=parsed_path["id"], project__owner=user)

        if update_data:
            service = await Service.objects.filter(
                id=parsed_path["id"], project__owner=user
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

    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def delete(self, parsed_path: Path[ServiceIdPath]) -> None:
        user = await self.request.auser()
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=user,
        )

        await service.adelete()
        return None


class ServiceCheckController(Controller[PydanticFastSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ServiceCheckResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def post(self, parsed_path: Path[ServiceIdPath]) -> HttpResponse:
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        import httpx
        import time

        start = time.monotonic()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(service.url, timeout=service.timeout)

                elapsed_ms = int((time.monotonic() - start) * 1000)

                result = (
                    "success"
                    if response.status_code == service.expected_status_code
                    else "unexpected_status"
                )

                return self.to_response(
                    ServiceCheckResponse(
                        service_id=str(service.id),
                        result=result,
                        status_code=response.status_code,
                        elapsed_time=elapsed_ms,
                    )
                )
            except httpx.TimeoutException:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                return self.to_response(
                    ServiceCheckResponse(
                        service_id=str(service.id),
                        result=result,
                        status_code=response.status_code,
                        elapsed_time=elapsed_ms,
                    )
                )

            except httpx.RequestError:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                return self.to_response(
                    ServiceCheckResponse(
                        service_id=str(service.id),
                        result=result,
                        status_code=response.status_code,
                        elapsed_time=elapsed_ms,
                    )
                )
