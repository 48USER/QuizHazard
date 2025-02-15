from aiogram.fsm.state import State, StatesGroup


class Register(StatesGroup):
    waiting_for_nickname = State()


class QuizCreation(StatesGroup):
    waiting_for_quiz_name = State()
    waiting_for_question = State()
    waiting_for_correct_answer = State()
    waiting_for_wrong_answer = State()
    waiting_for_next_question_decision = State()
    waiting_for_quiz_themes = State()


class OnQuiz(StatesGroup):
    waiting_for_nickname = State()
