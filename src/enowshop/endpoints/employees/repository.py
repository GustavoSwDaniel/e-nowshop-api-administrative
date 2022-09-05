from operator import or_
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from enowshop.infrastructure.repositories.repository import SqlRepository
from enowshop_models.models.employees import Employees
from enowshop_models.models.employees_phones import EmployeesPhones
from exception import RepositoryException


class EmployeesRepository(SqlRepository):
    model = Employees

    async def verify_email_or_cpf_already_register(self, email, cpf):
        async with self.session_factory() as session:
            result = await session.execute(
                select(self.model).where(or_(self.model.email == email, self.model.cpf == cpf))
            )
        if result.scalars().first():
            raise RepositoryException('That email or cpf is already registered')

    async def filter_by_with_address(self, params):
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(**params).options(
                selectinload(self.model.employees_phones)))
            return result.scalars().first()


class EmployeesPhonesRepository(SqlRepository):
    model = EmployeesPhones

    async def create_phones_with_bulk_operator(self, phones: List):
        async with self.session_factory() as session:
            model = session.add_all([self.model(**phone) for phone in phones])
            await session.commit()
            return model
