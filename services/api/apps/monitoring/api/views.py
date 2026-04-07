from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from django.db.models import Avg, Min, Max, Count, Q
from django.http import HttpResponse
from dmr import Controller, validate, ResponseSpec, Path
from dmr.plugins.pydantic import PydanticSerializer
from dmr.security.jwt import JWTAsyncAuth

from apps.accounts.api.schemas import AuthenticatedHttpRequest
from apps.monitoring.api.schemas import (
    HealthCheckInfo,
    HealthChecksResponse,
    UptimeResponse,
    ProjectStatusResponse,
    ServiceStatusInfo,
    ServiceIdPath,
    ProjectSlugPath,
)
from apps.monitoring.models import HealthCheck
from apps.projects.models import Service, Project


class HealthChecksController(Controller[PydanticSerializer]):
    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            HealthChecksResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ServiceIdPath]) -> HttpResponse:
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        page = int(self.request.GET.get("page", "1"))
        page_size = int(self.request.GET.get("page_size", "20"))
        date_from = self.request.GET.get("from")
        date_to = self.request.GET.get("to")

        qs = HealthCheck.objects.filter(service=service)

        if date_from:
            qs = qs.filter(checked_at__gte=date_from)
        if date_to:
            qs = qs.filter(checked_at__lte=date_to)

        total = await qs.acount()
        offset = (page - 1) * page_size

        checks = [
            HealthCheckInfo(
                id=str(hc.id),
                service_id=str(hc.service.id),
                result=hc.result,
                status_code=hc.status_code,
                response_time_ms=hc.response_time_ms,
                error_message=hc.error_message or "",
                checked_at=hc.checked_at,
            )
            async for hc in qs.order_by("-checked_at")[offset : offset + page_size]
        ]

        return self.to_response(
            HealthChecksResponse(
                checks=checks,
                total=total,
                page=page,
                page_size=page_size,
            )
        )


class UptimeController(Controller[PydanticSerializer]):

    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(
        ResponseSpec(
            UptimeResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ServiceIdPath]) -> HttpResponse:
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        period = self.request.GET.get("period", "24h")
        period_map = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
        }
        delta = period_map.get(period, timedelta(hours=24))
        since = datetime.now(timezone.utc) - delta

        qs = HealthCheck.objects.filter(
            service=service,
            checked_at__gte=since,
        )

        stats = await qs.aaggregate(
            total=Count("id"),
            successful=Count("id", filter=Q(result="success")),
            avg_rt=Avg("response_time_ms"),
            min_rt=Min("response_time_ms"),
            max_rt=Max("response_time_ms"),
        )

        total = stats["total"] or 0
        successful = stats["successful"] or 0
        uptime_percent = (successful / total * 100) if total > 0 else 0.0

        return self.to_response(
            UptimeResponse(
                service_id=str(service.id),
                period=period,
                uptime_percent=round(uptime_percent, 2),
                avg_response_time_ms=int(stats["avg_rt"] or 0),
                min_response_time_ms=int(stats["min_rt"] or 0),
                max_response_time_ms=int(stats["max_rt"] or 0),
                total_checks=total,
            )
        )


class ProjectStatusController(Controller[PydanticSerializer]):

    @validate(
        ResponseSpec(
            ProjectStatusResponse,
            status_code=HTTPStatus.OK,
        )
    )
    async def get(self, parsed_path: Path[ProjectSlugPath]) -> HttpResponse:
        project = await Project.objects.aget(slug=parsed_path["slug"])
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        services = []
        async for service in Service.objects.filter(
            project=project,
            is_active=True,
        ):
            stats = await HealthCheck.objects.filter(
                service=service,
                checked_at__gte=since,
            ).aaggregate(
                total=Count("id"),
                successful=Count("id", filter=Q(result="success")),
                avg_rt=Avg("response_time_ms"),
            )

            total = stats["total"] or 0
            successful = stats["successful"] or 0
            uptime = (successful / total * 100) if total > 0 else 0.0

            services.append(
                ServiceStatusInfo(
                    id=str(service.id),
                    name=service.name,
                    current_status=service.current_status,
                    uptime_24h_percent=round(uptime, 2),
                    avg_response_time_ms=int(stats["avg_rt"] or 0),
                )
            )

        return self.to_response(
            ProjectStatusResponse(
                project_name=project.name,
                project_slug=project.slug,
                services=services,
            )
        )
