from dmr.routing import Router, path

from apps.alerts.api.views import (
    AlertRulesController,
    AlertRuleDetailsController,
    AlertEventsController,
)

alert_rules_router = Router(
    prefix="services/",
    urls=[
        path(
            "<uuid:id>/alerts/rules/",
            AlertRulesController.as_view(),
            name="alert_rules",
        ),
    ],
)

alert_management_router = Router(
    prefix="alerts/",
    urls=[
        path(
            "rules/<uuid:id>/",
            AlertRuleDetailsController.as_view(),
            name="alert_rule_details",
        ),
        path(
            "events/",
            AlertEventsController.as_view(),
            name="alert_events",
        ),
    ],
)
