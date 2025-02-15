from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import database.requests as rqsts
from keyboards.base_kb import (
    starting_quiz_kb,
)
from states.base_states import OnQuiz

quiz_selector_router = Router()


@quiz_selector_router.message(F.text == "Пройти Квиз")
async def handle_pass_quiz(message: Message):
    await message.answer("Выберите тип квиза:", reply_markup=starting_quiz_kb)


@quiz_selector_router.message(F.text == "Случайный Квиз")
async def handle_random_quiz(message: Message, state: FSMContext):
    quiz = await rqsts.get_random_quiz()
    if quiz is None:
        await message.answer("Нет доступных квизов.")
        return
    await state.set_state(OnQuiz.waiting_for_answer)
    await message.answer(
        f"Начинаем квиз: {quiz.title}.\n"
        "Начинайте отвечать на вопросы. (Функционал квиза пока не готов)"
    )


@quiz_selector_router.message(F.text == "Популярные Квизы")
async def handle_popular_quizzes(message: Message):
    quizzes = await rqsts.get_popular_quizzes(limit=3)
    if not quizzes:
        await message.answer("Нет популярных квизов.")
        return

    response = "Популярные квизы:\n"
    for quiz in quizzes:
        themes_str = ", ".join([theme.name for theme in quiz.themes])
        response += f"ID: {quiz.id} - {quiz.title} (Темы: {themes_str})\n"
    await message.answer(response)
