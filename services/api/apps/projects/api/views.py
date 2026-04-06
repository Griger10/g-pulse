from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, validate, ResponseSpec, Body, Path
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security.jwt import JWTAsyncAuth
from slugify import slugify

from apps.accounts.api.schemas import AuthenticatedHttpRequest
from apps.projects.api.schemas import (
    ProjectsResponse,
    ProjectInfo,
    ProjectInfoCreate,
    ProjectDetailsPath,
)
from apps.projects.models import Project


class ProjectsController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            ProjectsResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self) -> HttpResponse:
        return self.to_response(
            ProjectsResponse(
                projects=[
                    ProjectInfo(
                        id=str(project.id),
                        name=project.name,
                        slug=project.slug,
                        description=project.description,
                        created_at=project.created_at,
                        updated_at=project.updated_at,
                    )
                    async for project in Project.objects.filter(owner=self.request.user)
                ]
            )
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
            owner=self.request.user.id,
        )

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
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
    async def get(self, parsed_path: Path[ProjectDetailsPath]) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
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
    async def put(
        self,
        parsed_path: Path[ProjectDetailsPath],
        parsed_body: Body[ProjectInfoCreate],
    ) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )
        update_data = {
            field: value for field, value in parsed_body.model_dump().items()
        }

        if update_data:
            project = await Project.objects.filter(
                id=project.id, owner=self.request.user
            ).aupdate(**update_data)

        return self.to_response(
            ProjectInfo(
                id=str(project.id),
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
            status_code=HTTPStatus.NO_CONTENT,
        )
    )
    async def delete(self, parsed_path: Path[ProjectDetailsPath]) -> HttpResponse:
        project = await Project.objects.aget(
            slug=parsed_path["slug"],
            owner=self.request.user,
        )
        await project.adelete()
        return self.to_response(status_code=HTTPStatus.NO_CONTENT)
