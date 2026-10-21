from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from app.repositories.premium import activate_premium, payment_history, premium_status
from app.services.premium import PLANS, get_plan, payment_payload, plan_from_payload

router = Router(name="payments")


@router.message(Command("plans"))
async def plans_command(message: Message) -> None:
    lines = [f"{plan.title}: {plan.stars} Stars / {plan.days} days" for plan in PLANS]
    await message.answer("Premium plans:\n" + "\n".join(lines) + "\n\nUse /buy <plan_id>.")


@router.message(Command("buy"))
async def buy_command(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /buy monthly or /buy quarterly")
        return
    plan = get_plan(parts[1].strip().casefold())
    if plan is None:
        await message.answer("Unknown plan. Use /plans to see the available plans.")
        return
    await message.answer_invoice(
        title=plan.title,
        description=f"{plan.days} days of MultiFilterBot Premium access.",
        payload=payment_payload(plan.plan_id),
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=plan.title, amount=plan.stars)],
    )


@router.message(Command("myplan"))
async def my_plan_command(message: Message) -> None:
    if message.from_user is None:
        return
    expires_at = await premium_status(message.from_user.id)
    if expires_at is None:
        await message.answer("You do not have an active Premium plan.")
        return
    remaining = max(1, (expires_at - datetime.now(timezone.utc)).days)
    warning = "\n⚠️ Your plan expires soon." if remaining <= 3 else ""
    await message.answer(f"Your Premium plan is active until {expires_at:%Y-%m-%d %H:%M} UTC.\nRemaining: {remaining} day(s).{warning}")


@router.message(Command("paymenthistory"))
async def payment_history_command(message: Message) -> None:
    if message.from_user is None:
        return
    payments = await payment_history(message.from_user.id)
    if not payments:
        await message.answer("No Premium payments found.")
        return
    lines = []
    for item in payments:
        created = item.get("created_at")
        date = created.strftime("%Y-%m-%d") if created else "unknown date"
        expiry = item.get("expires_at")
        expiry_text = expiry.strftime("%Y-%m-%d") if expiry else "pending"
        lines.append(f"- {item.get('plan_id', 'premium')} on {date}; expires {expiry_text}")
    await message.answer("Premium payment history:\n" + "\n".join(lines))


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery) -> None:
    plan = plan_from_payload(query.invoice_payload)
    if plan is None:
        await query.answer(ok=False, error_message="This Premium plan is no longer available.")
        return
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    if message.from_user is None or message.successful_payment is None:
        return
    plan = plan_from_payload(message.successful_payment.invoice_payload)
    if plan is None:
        await message.answer("Payment received, but the plan could not be identified. Contact support.")
        return
    expires_at = await activate_premium(
        user_id=message.from_user.id,
        plan_id=plan.plan_id,
        days=plan.days,
        charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    if expires_at is None:
        await message.answer("This payment has already been processed.")
        return
    await message.answer(f"Premium activated until {expires_at:%Y-%m-%d %H:%M} UTC.")
