from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import database.requests as rqsts
import keyboards.base_kb as kbs
import states.base_states as states

cmd_router = Router()


@cmd_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user = await rqsts.get_user(message.from_user.id)
    if user is None:
        ans = f"Привет, {html.bold(message.from_user.full_name)}!\n"
        ans += "Для начала, придумай себе никнейм:"
        await message.answer(
            text=ans,
        )
        await state.set_state(states.Register.waiting_for_nickname)
    else:
        await message.answer(
            f"С возвращением, {html.bold(user.nickname)}!", reply_markup=kbs.main_kb
        )


@cmd_router.message(states.Register.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext) -> None:
    nickname = message.text.strip()
    if await rqsts.get_user_by_nickname(nickname):
        await message.answer("Этот никнейм уже занят. Пожалуйста, выберите другой:")
        return
    await rqsts.create_user(tg_id=message.from_user.id, nickname=nickname)
    await message.answer(
        f"Регистрация прошла успешно, {html.bold(nickname)}!", reply_markup=kbs.main_kb
    )
    await state.clear()
