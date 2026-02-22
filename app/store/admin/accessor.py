from hashlib import sha256
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        if not app.config.admin:
            return

        admin_config = app.config.admin
        existing_admin = await self.get_by_email(admin_config.email)
        if existing_admin is None:
            await self.create_admin(admin_config.email, admin_config.password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        if not self.app.database.session:
            return None

        async with self.app.database.session() as session:
            result = await session.scalar(
                select(AdminModel).where(AdminModel.email == email)
            )
            return result

    async def get_by_id(self, id_: int) -> AdminModel | None:
        if not self.app.database.session:
            return None

        async with self.app.database.session() as session:
            result = await session.scalar(
                select(AdminModel).where(AdminModel.id == id_)
            )
            return result

    async def create_admin(self, email: str, password: str) -> AdminModel:
        if not self.app.database.session:
            raise RuntimeError("Database session is not initialized")

        hashed_password = sha256(password.encode()).hexdigest()
        admin = AdminModel(email=email, password=hashed_password)

        async with self.app.database.session() as session:
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            return admin
