from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пройти Квиз"),
        ],
        [
            KeyboardButton(text="Мои квизы"),
            KeyboardButton(text="Мой профиль"),
        ],
    ],
    resize_keyboard=True,
)


starting_quiz_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Случайный Квиз"),
            KeyboardButton(text="Популярные Квизы"),
        ],
        [
            KeyboardButton(text="Подписки"),
            KeyboardButton(text="Поиск"),
        ],
    ],
    resize_keyboard=True,
)


search_quiz_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Название"),
            KeyboardButton(text="Автор"),
        ],
        [
            KeyboardButton(text="Тема"),
            KeyboardButton(text="Id"),
        ],
    ],
    input_field_placeholder="Искать по ...",
    resize_keyboard=True,
)

my_quizes_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить Квиз"),
            KeyboardButton(text="Удалить Квиз"),
        ],
        [
            KeyboardButton(text="Статистика"),
        ],
    ],
    resize_keyboard=True,
)

new_quiz_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="QuizBuilder"),
            KeyboardButton(text="Загрузить готовый"),
        ],
    ],
    resize_keyboard=True,
)

profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Изменить имя"),
            KeyboardButton(text="Donation info"),
        ],
        [
            KeyboardButton(text="История"),
        ],
    ],
    resize_keyboard=True,
)
