from operator import or_
from typing import List, Dict

from sqlalchemy import select, func
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

    async def get_all_employees(self, params: Dict):
        async with self.session_factory() as session:
            results = await session.execute(select(self.model).limit(params.get('limit')).offset(params.get('offset')))
            total = await session.execute(select([func.count(self.model.id)]).select_from(self.model))

            total = total.scalar()
            results = results.scalars().all()

        return results, total

    async def get_employment_info_by_email(self, params) -> Employees:
        async with self.session_factory() as session:
            result = await session.execute(select(self.model).filter_by(**params))
            result = result.scalars().first()

        if not result:
            raise RepositoryException('Email not already registered')

        return result


class EmployeesPhonesRepository(SqlRepository):
    model = EmployeesPhones

    async def create_phones_with_bulk_operator(self, phones: List):
        async with self.session_factory() as session:
            model = session.add_all([self.model(**phone) for phone in phones])
            await session.commit()
            return model
