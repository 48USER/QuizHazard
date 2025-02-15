from sqlalchemy import desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from database.models import Question, Quiz, Theme, User, async_session


async def get_user(tg_id: int):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_user_by_nickname(nickname: str):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.nickname == nickname))


async def create_user(tg_id: int, nickname: str, donation_info: str = ""):
    async with async_session() as session:
        user = User(tg_id=tg_id, nickname=nickname, donation_info=donation_info)
        session.add(user)
        await session.commit()
        return user


async def create_quiz(
    tg_id: int, quiz_name: str, quiz_questions: list, quiz_themes: list
):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise ValueError("Пользователь не найден")

        theme_objs = []
        if quiz_themes:
            theme_query = await session.scalars(
                select(Theme).where(Theme.name.in_(quiz_themes))
            )
            theme_objs = list(theme_query)

        quiz = Quiz(title=quiz_name, creator_id=user.id, themes=theme_objs)

        questions = []
        for q in quiz_questions:
            wrong_answers = q.get("wrong_answers", [])
            wrong_answer_1 = wrong_answers[0] if len(wrong_answers) > 0 else None
            wrong_answer_2 = wrong_answers[1] if len(wrong_answers) > 1 else None
            wrong_answer_3 = wrong_answers[2] if len(wrong_answers) > 2 else None

            question = Question(
                question_text=q.get("question_text"),
                image=q.get("photo"),
                correct_answer=q.get("correct_answer"),
                wrong_answer_1=wrong_answer_1,
                wrong_answer_2=wrong_answer_2,
                wrong_answer_3=wrong_answer_3,
                quiz=quiz,
            )
            questions.append(question)

        quiz.questions = questions

        session.add(quiz)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e

        return quiz


async def get_quizzes(limit: int = 10):
    async with async_session() as session:
        result = await session.scalars(select(Quiz).limit(limit))
        quizzes = result.all()
        return quizzes


async def get_popular_quizzes(limit: int = 3):
    async with async_session() as session:
        result = await session.scalars(
            select(Quiz)
            .options(selectinload(Quiz.themes))
            .order_by(desc(Quiz.rating))
            .limit(limit)
        )
        quizzes = result.all()
        return quizzes
