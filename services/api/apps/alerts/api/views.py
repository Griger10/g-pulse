from http import HTTPStatus

from django.http import HttpResponse
from dmr import Controller, validate, ResponseSpec, Body, Path, modify
from dmr.plugins.pydantic import PydanticFastSerializer
from dmr.security.jwt import JWTAsyncAuth

from apps.accounts.api.schemas import AuthenticatedHttpRequest
from apps.alerts.api.schemas import (
    AlertRuleInfo,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertEventInfo,
    AlertEventsResponse,
    ServiceIdPath,
    AlertRuleIdPath,
)
from apps.alerts.models import AlertRule, AlertEvent
from apps.projects.models import Service


class AlertRulesController(Controller[PydanticFastSerializer]):

    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(ResponseSpec(list[AlertRuleInfo], status_code=HTTPStatus.OK))
    async def get(self, parsed_path: Path[ServiceIdPath]) -> HttpResponse:
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        rules = [
            AlertRuleInfo(
                id=str(rule.id),
                service_id=str(rule.service.id),
                condition=rule.condition,
                threshold=rule.threshold,
                transport=rule.transport,
                is_active=rule.is_active,
                cooldown_minutes=rule.cooldown_minutes,
                created_at=rule.created_at,
            )
            async for rule in AlertRule.objects.filter(
                service=service,
                owner=self.request.user,
            )
        ]

        return self.to_response(rules)

    @validate(ResponseSpec(AlertRuleInfo, status_code=HTTPStatus.CREATED))
    async def post(
        self,
        parsed_path: Path[ServiceIdPath],
        parsed_body: Body[AlertRuleCreate],
    ) -> HttpResponse:
        service = await Service.objects.aget(
            id=parsed_path["id"],
            project__owner=self.request.user,
        )

        rule = await AlertRule.objects.acreate(
            service=service,
            owner=self.request.user,
            condition=parsed_body.condition,
            threshold=parsed_body.threshold,
            transport=parsed_body.transport,
            cooldown_minutes=parsed_body.cooldown_minutes,
            is_active=parsed_body.is_active,
        )

        return self.to_response(
            AlertRuleInfo(
                id=str(rule.id),
                service_id=str(rule.service.id),
                condition=rule.condition,
                threshold=rule.threshold,
                transport=rule.transport,
                is_active=rule.is_active,
                cooldown_minutes=rule.cooldown_minutes,
                created_at=rule.created_at,
            ),
            status_code=HTTPStatus.CREATED,
        )


class AlertRuleDetailsController(Controller[PydanticFastSerializer]):

    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(ResponseSpec(AlertRuleInfo, status_code=HTTPStatus.OK))
    async def patch(
        self,
        parsed_path: Path[AlertRuleIdPath],
        parsed_body: Body[AlertRuleUpdate],
    ) -> HttpResponse:
        rule = await AlertRule.objects.aget(
            id=parsed_path["id"],
            owner=self.request.user,
        )

        update_data = {
            field: value
            for field, value in parsed_body.model_dump().items()
            if value is not None
        }

        if update_data:
            await AlertRule.objects.filter(id=rule.id, owner=self.request.user).aupdate(
                **update_data
            )
            rule = await AlertRule.objects.aget(id=rule.id)

        return self.to_response(
            AlertRuleInfo(
                id=str(rule.id),
                service_id=str(rule.service.id),
                condition=rule.condition,
                threshold=rule.threshold,
                transport=rule.transport,
                is_active=rule.is_active,
                cooldown_minutes=rule.cooldown_minutes,
                created_at=rule.created_at,
            )
        )

    @modify(status_code=HTTPStatus.NO_CONTENT)
    async def delete(self, parsed_path: Path[AlertRuleIdPath]) -> None:
        rule = await AlertRule.objects.aget(
            id=parsed_path["id"],
            owner=self.request.user,
        )
        await rule.adelete()
        return None


class AlertEventsController(Controller[PydanticFastSerializer]):

    request: AuthenticatedHttpRequest
    auth = (JWTAsyncAuth(),)

    @validate(ResponseSpec(AlertEventsResponse, status_code=HTTPStatus.OK))
    async def get(self) -> HttpResponse:
        page = int(self.request.GET.get("page", "1"))
        page_size = int(self.request.GET.get("page_size", "20"))
        service_id = self.request.GET.get("service_id")

        qs = AlertEvent.objects.filter(rule__owner=self.request.user)

        if service_id:
            qs = qs.filter(service_id=service_id)

        total = await qs.acount()
        offset = (page - 1) * page_size

        events = [
            AlertEventInfo(
                id=str(event.id),
                rule_id=str(event.rule.id),
                service_id=str(event.service.id),
                status=event.status,
                message=event.message,
                created_at=event.created_at,
            )
            async for event in qs.order_by("-created_at")[offset : offset + page_size]
        ]

        return self.to_response(
            AlertEventsResponse(
                events=events,
                total=total,
                page=page,
                page_size=page_size,
            )
        )
