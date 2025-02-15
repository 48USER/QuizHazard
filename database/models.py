from typing import List, Optional

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nickname: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)

    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", back_populates="creator", cascade="all, delete-orphan"
    )

    donation_info: Mapped[str] = mapped_column(String(120), nullable=False, default="")


quiz_theme_association = Table(
    "quiz_theme",
    Base.metadata,
    Column("quiz_id", ForeignKey("quizzes.id"), primary_key=True),
    Column("theme_id", ForeignKey("themes.id"), primary_key=True),
)


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz", secondary=quiz_theme_association, back_populates="themes"
    )


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["User"] = relationship("User", back_populates="quizzes")
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )
    themes: Mapped[List["Theme"]] = relationship(
        "Theme", secondary=quiz_theme_association, back_populates="quizzes"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), nullable=False)

    question_text: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String, nullable=False)
    wrong_answer_1: Mapped[str] = mapped_column(String, nullable=False)
    wrong_answer_2: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    wrong_answer_3: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
