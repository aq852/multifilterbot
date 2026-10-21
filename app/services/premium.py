from dataclasses import dataclass


@dataclass(frozen=True)
class PremiumPlan:
    plan_id: str
    title: str
    days: int
    stars: int


PLANS = (
    PremiumPlan("monthly", "Monthly Premium", 30, 100),
    PremiumPlan("quarterly", "Quarterly Premium", 90, 250),
)


def get_plan(plan_id: str) -> PremiumPlan | None:
    return next((plan for plan in PLANS if plan.plan_id == plan_id), None)


def payment_payload(plan_id: str) -> str:
    return f"premium:{plan_id}"


def plan_from_payload(payload: str) -> PremiumPlan | None:
    prefix, separator, plan_id = payload.partition(":")
    if prefix != "premium" or not separator:
        return None
    return get_plan(plan_id)

