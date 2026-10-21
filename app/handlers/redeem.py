from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.access import is_admin
from app.repositories.premium import activate_premium
from app.repositories.redeem import claim_redeem_code, create_redeem_code
from app.services.redeem import normalize_code, redeem_charge_id

router = Router(name="redeem")


@router.message(Command("createcode"))
async def create_code_command(message: Message) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        await message.answer("You are not authorized to use this command.")
        return
    parts = (message.text or "").split()
    if len(parts) not in {3, 4}:
        await message.answer("Usage: /createcode <code> <days> [uses]")
        return
    try:
        days = int(parts[2])
        uses = int(parts[3]) if len(parts) == 4 else 1
    except ValueError:
        await message.answer("Days and uses must be whole numbers.")
        return
    code = normalize_code(parts[1])
    if not await create_redeem_code(code, days, uses):
        await message.answer("Code is invalid or already exists.")
        return
    await message.answer(f"Redeem code created: {code} ({days} days, {uses} uses).")


@router.message(Command("redeem"))
async def redeem_command(message: Message) -> None:
    if message.from_user is None:
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /redeem <code>")
        return
    code = normalize_code(parts[1])
    claimed = await claim_redeem_code(code, message.from_user.id)
    if claimed is None:
        await message.answer("This code is invalid, expired, exhausted, or already used by you.")
        return
    expires_at = await activate_premium(
        user_id=message.from_user.id,
        plan_id=f"redeem:{code}",
        days=claimed["days"],
        charge_id=redeem_charge_id(code, message.from_user.id),
    )
    if expires_at is None:
        await message.answer("This redemption was already processed.")
        return
    await message.answer(f"Redeemed successfully. Premium is active until {expires_at:%Y-%m-%d %H:%M} UTC.")

