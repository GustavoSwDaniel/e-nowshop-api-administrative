from typing import Dict

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.endpoints.employees.repository import EmployeesRepository, EmployeesPhonesRepository
from enowshop.endpoints.employees.schema import LoginSchema
from enowshop_models.models.users import Users


class EmployeesService:
    def __init__(self, employees_repository: EmployeesRepository,
                 employees_phones_repository: EmployeesPhonesRepository,
                 keycloak_service: KeycloakService,):
        self.employees_repo = employees_repository
        self.employees_phones_repo = employees_phones_repository
        self.keycloak_service = keycloak_service

    async def check_if_email_or_cpf_already_registered(self, email: str, cpf: str):
        await self.employees_repo.verify_email_or_cpf_already_register(email=email, cpf=cpf)

    async def register_employees(self, user_data: Dict):
        password = user_data.pop('password')
        address = user_data.pop('address')
        phones = user_data.pop('phones')
        user = await self.employees_repo.create(user_data)
        address['user_id'] = user.id
        list(map(lambda item: item.update({'user_id': user.id}), phones))
        await self.employees_phones_repo.create_phones_with_bulk_operator(phones)

        keycloak_uuid = await self.keycloak_service.create_user_by_admin_cli(data=user_data, password=password,
                                                                             employee_id=user.id)

        await self.employees_repo.update(pk=user.id, values={'keycloak': keycloak_uuid})

    async def login(self, login_data: LoginSchema) -> Dict:
        response = await self.keycloak_service.auth_user(username=login_data.username,
                                                         password=login_data.password)
        return response

