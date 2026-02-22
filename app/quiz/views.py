from aiohttp.web_exceptions import HTTPBadRequest, HTTPConflict, HTTPNotFound
from aiohttp_apispec import querystring_schema, request_schema, response_schema

from app.quiz.models import AnswerModel
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import error_json_response, json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        data = self.request.get("data", {})
        title = data.get("title")

        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            return error_json_response(
                http_status=409,
                status="conflict",
                message="Theme with this title already exists",
            )

        theme = await self.store.quizzes.create_theme(title)
        return json_response(data={"id": theme.id, "title": theme.title})


class ThemeListView(AuthRequiredMixin, View):
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        themes_data = [{"id": theme.id, "title": theme.title} for theme in themes]
        return json_response(data={"themes": themes_data})


class QuestionAddView(AuthRequiredMixin, View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = self.request.get("data", {})
        title = data.get("title")
        theme_id = data.get("theme_id")
        answers_data = data.get("answers", [])

        # Валидация: хотя бы один правильный ответ
        correct_answers = [a for a in answers_data if a.get("is_correct", False)]
        if len(correct_answers) == 0:
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="At least one answer must be correct",
            )

        # Валидация: только один правильный ответ
        if len(correct_answers) > 1:
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="Only one answer can be correct",
            )

        # Валидация: минимум два ответа
        if len(answers_data) < 2:
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="Question must have at least two answers",
            )

        # Проверка существования темы
        theme = await self.store.quizzes.get_theme_by_id(theme_id)
        if not theme:
            return error_json_response(
                http_status=404,
                status="not_found",
                message="Theme not found",
            )

        # Проверка уникальности вопроса
        existing_question = await self.store.quizzes.get_question_by_title(title)
        if existing_question:
            return error_json_response(
                http_status=409,
                status="conflict",
                message="Question with this title already exists",
            )

        # Создание ответов
        answers = [
            AnswerModel(title=answer["title"], is_correct=answer["is_correct"])
            for answer in answers_data
        ]

        question = await self.store.quizzes.create_question(title, theme_id, answers)

        answers_response = [
            {"title": answer.title, "is_correct": answer.is_correct}
            for answer in question.answers
        ]

        return json_response(
            data={
                "id": question.id,
                "title": question.title,
                "theme_id": question.theme_id,
                "answers": answers_response,
            }
        )


class QuestionListView(AuthRequiredMixin, View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        theme_id = int(theme_id) if theme_id else None

        questions = await self.store.quizzes.list_questions(theme_id=theme_id)

        questions_data = []
        for question in questions:
            answers_data = [
                {"title": answer.title, "is_correct": answer.is_correct}
                for answer in question.answers
            ]
            questions_data.append(
                {
                    "id": question.id,
                    "title": question.title,
                    "theme_id": question.theme_id,
                    "answers": answers_data,
                }
            )

        return json_response(data={"questions": questions_data})
