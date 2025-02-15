from typing import List, Union

from aiogram import F, Router, html
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import database.requests as rqsts
from config import THEMES
from states.base_states import QuizCreation

quiz_builder_router = Router()


async def _finish_wrong_answers(
    event: Union[Message, CallbackQuery], state: FSMContext
):
    data = await state.get_data()
    wrong_answers: List[str] = data.get("wrong_answers", [])

    if not wrong_answers:
        if isinstance(event, CallbackQuery):
            await event.answer(
                "Добавьте хотя бы один неправильный ответ.", show_alert=True
            )
        else:
            await event.reply("Добавьте хотя бы один неправильный ответ.")
        return

    question_data = {
        "question_text": data.get("question_text"),
        "photo": data.get("question_photo"),
        "correct_answer": data.get("correct_answer"),
        "wrong_answers": wrong_answers,
    }
    quiz_questions: List[dict] = data.get("quiz_questions", [])
    quiz_questions.append(question_data)
    await state.update_data(quiz_questions=quiz_questions)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Добавить следующий вопрос", callback_data="add_next_question"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Закончить создание квиза",
                    callback_data="finish_quiz_creation",
                )
            ],
        ]
    )
    text = "Вопрос добавлен. Что хотите делать дальше?"

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.reply(text, reply_markup=keyboard)

    await state.set_state(QuizCreation.waiting_for_next_question_decision)


@quiz_builder_router.message(F.text == "QuizBuilder")
async def start_quiz_creation(message: Message, state: FSMContext):
    await state.set_state(QuizCreation.waiting_for_quiz_name)
    await message.answer("Введите название квиза:")


@quiz_builder_router.message(QuizCreation.waiting_for_quiz_name)
async def process_quiz_name(message: Message, state: FSMContext):
    quiz_name = message.text.strip()
    if not quiz_name:
        await message.answer("Название не может быть пустым. Введите название квиза:")
        return
    await state.update_data(quiz_name=quiz_name, current_question=1, quiz_questions=[])
    await message.answer(
        f"Квиз '{html.bold(quiz_name)}' создан.\n"
        "Теперь добавьте первый вопрос, отправив сообщение: 'Добавить вопрос'."
    )
    await state.set_state(QuizCreation.waiting_for_question)


@quiz_builder_router.message(F.text == "Добавить вопрос")
async def start_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data.get("current_question", 1)
    await message.answer(
        f"Укажите вопрос номер {current_question}.\n(При необходимости прикрепите картинку)"
    )
    await state.set_state(QuizCreation.waiting_for_question)


@quiz_builder_router.message(QuizCreation.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    question_text = message.text or ""
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id

    await state.update_data(
        question_text=question_text,
        question_photo=photo,
    )
    await message.answer("Укажите правильный ответ:")
    await state.set_state(QuizCreation.waiting_for_correct_answer)


@quiz_builder_router.message(QuizCreation.waiting_for_correct_answer)
async def process_correct_answer(message: Message, state: FSMContext):
    correct_answer = message.text.strip()
    await state.update_data(correct_answer=correct_answer, wrong_answers=[])
    await message.answer(
        "Укажите неправильный ответ.\nОтправьте текст или нажмите кнопку «Готово», если вариантов достаточно.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Готово", callback_data="wrong_answers_done"
                    )
                ]
            ]
        ),
    )
    await state.set_state(QuizCreation.waiting_for_wrong_answer)


@quiz_builder_router.message(QuizCreation.waiting_for_wrong_answer)
async def process_wrong_answer(message: Message, state: FSMContext):
    wrong_answer = message.text.strip()
    data = await state.get_data()
    wrong_answers: List[str] = data.get("wrong_answers", [])

    if len(wrong_answers) >= 3:
        await message.answer("Достигнуто максимальное количество неправильных ответов.")
        return await _finish_wrong_answers(message, state)

    wrong_answers.append(wrong_answer)
    await state.update_data(wrong_answers=wrong_answers)

    await message.answer(
        f"Текущие неправильные ответы: {', '.join(wrong_answers)}.\n"
        "Введите следующий неправильный ответ или нажмите кнопку «Готово».",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Готово", callback_data="wrong_answers_done"
                    )
                ]
            ]
        ),
    )


@quiz_builder_router.callback_query(
    F.data == "wrong_answers_done", StateFilter(QuizCreation.waiting_for_wrong_answer)
)
async def finish_wrong_answers_callback(callback: CallbackQuery, state: FSMContext):
    await _finish_wrong_answers(callback, state)


@quiz_builder_router.callback_query(
    F.data == "add_next_question",
    StateFilter(QuizCreation.waiting_for_next_question_decision),
)
async def add_next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data.get("current_question", 1) + 1
    await state.update_data(current_question=current_question)
    await callback.message.edit_text(
        f"Укажите вопрос номер {current_question}.\n(При необходимости прикрепите картинку)"
    )
    await state.set_state(QuizCreation.waiting_for_question)
    await callback.answer()


@quiz_builder_router.callback_query(
    F.data == "finish_quiz_creation",
    StateFilter(QuizCreation.waiting_for_next_question_decision),
)
async def ask_for_quiz_themes(callback: CallbackQuery, state: FSMContext):
    def chunk(
        lst: List[InlineKeyboardButton], n: int
    ) -> List[List[InlineKeyboardButton]]:
        return [lst[i : i + n] for i in range(0, len(lst), n)]

    buttons = [
        InlineKeyboardButton(text=theme, callback_data=f"quiz_theme_{theme}")
        for theme in THEMES
    ]
    rows = chunk(buttons, 2)
    rows.append([InlineKeyboardButton(text="Готово", callback_data="quiz_theme_done")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    await callback.message.edit_text("Укажите темы для квиза:", reply_markup=keyboard)
    await state.set_state(QuizCreation.waiting_for_quiz_themes)
    await callback.answer()


@quiz_builder_router.callback_query(
    F.data.startswith("quiz_theme_"), StateFilter(QuizCreation.waiting_for_quiz_themes)
)
async def process_quiz_theme_selection(callback: CallbackQuery, state: FSMContext):
    data_value = callback.data
    state_data = await state.get_data()
    selected_themes: List[str] = state_data.get("quiz_themes", [])

    if data_value == "quiz_theme_done":
        if not selected_themes:
            await callback.answer("Выберите хотя бы одну тему.", show_alert=True)
            return
        quiz_questions = state_data.get("quiz_questions", [])
        quiz_name = state_data.get("quiz_name", "Без названия")
        await rqsts.create_quiz(
            tg_id=callback.from_user.id,
            quiz_name=quiz_name,
            quiz_questions=quiz_questions,
            quiz_themes=selected_themes,
        )
        await callback.message.edit_text(
            f"Квиз '{quiz_name}' создан с {len(quiz_questions)} вопросами и темами: {', '.join(selected_themes)}"
        )
        await state.clear()
        await callback.answer()
    else:
        theme = data_value[len("quiz_theme_") :]
        if theme in selected_themes:
            selected_themes.remove(theme)
        else:
            selected_themes.append(theme)
        await state.update_data(quiz_themes=selected_themes)
        await callback.answer(f"Текущий выбор тем: {', '.join(selected_themes)}")
