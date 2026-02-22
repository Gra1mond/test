from collections.abc import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    AnswerModel,
    QuestionModel,
    ThemeModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        if not self.app.database.session:
            raise RuntimeError("Database session is not initialized")

        theme = ThemeModel(title=title)
        async with self.app.database.session() as session:
            session.add(theme)
            await session.commit()
            await session.refresh(theme)
            return theme

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        if not self.app.database.session:
            return None

        async with self.app.database.session() as session:
            result = await session.scalar(
                select(ThemeModel).where(ThemeModel.title == title)
            )
            return result

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        if not self.app.database.session:
            return None

        async with self.app.database.session() as session:
            result = await session.scalar(
                select(ThemeModel).where(ThemeModel.id == id_)
            )
            return result

    async def list_themes(self) -> Sequence[ThemeModel]:
        if not self.app.database.session:
            return []

        async with self.app.database.session() as session:
            result = await session.scalars(select(ThemeModel))
            return list(result.all())

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        if not self.app.database.session:
            raise RuntimeError("Database session is not initialized")

        question = QuestionModel(title=title, theme_id=theme_id)
        answers_list = list(answers)

        async with self.app.database.session() as session:
            question.answers = answers_list
            session.add(question)
            await session.flush()
            await session.refresh(question, ["answers"])
            await session.commit()
            return question

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        if not self.app.database.session:
            return None

        async with self.app.database.session() as session:
            result = await session.scalar(
                select(QuestionModel).where(QuestionModel.title == title)
            )
            return result

    async def list_questions(
        self, theme_id: int | None = None
    ) -> Sequence[QuestionModel]:
        if not self.app.database.session:
            return []

        async with self.app.database.session() as session:
            query = select(QuestionModel).options(selectinload(QuestionModel.answers))
            if theme_id is not None:
                query = query.where(QuestionModel.theme_id == theme_id)
            result = await session.scalars(query)
            return list(result.all())
