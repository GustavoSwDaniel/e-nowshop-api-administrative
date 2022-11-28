from datetime import datetime
from typing import Dict

from enowshop_models.models.employees import Employees

from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.endpoints.employees.repository import EmployeesPhonesRepository
from enowshop.endpoints.employees.repository import EmployeesRepository
from enowshop.endpoints.paginate import paginate


class ManagerService:
    def __init__(self, employees_repository: EmployeesRepository,
                 employees_phones_repository: EmployeesPhonesRepository,
                 keycloak_service: KeycloakService, ):
        self.employees_repo = employees_repository
        self.employees_phones_repo = employees_phones_repository
        self.keycloak_service = keycloak_service

    async def check_if_email_or_cpf_already_registered(self, email: str, cpf: str):
        await self.employees_repo.verify_email_or_cpf_already_register(email=email, cpf=cpf)

    async def register_employees(self, employee_data: Dict):
        await self.check_if_email_or_cpf_already_registered(email=employee_data.get('email'),
                                                            cpf=employee_data.get('cpf'))

        password = employee_data.pop('password')
        phones = employee_data.pop('phones')
        employee_data['admission_date'] = datetime.now()
        employee = await self.employees_repo.create(employee_data)
        list(map(lambda item: item.update({'employees_id': employee.id}), phones))
        await self.employees_phones_repo.create_phones_with_bulk_operator(phones)

        keycloak_uuid = await self.keycloak_service.create_user_by_admin_cli(data=employee_data, password=password,
                                                                             employee_id=employee.id)

        await self.employees_repo.update(pk=employee.id, values={'keycloak_uuid': keycloak_uuid})

    async def login(self, login_data) -> Dict:
        response = await self.keycloak_service.auth_manager(username=login_data.username,
                                                            password=login_data.password)
        user_data = await self.employees_repo.get_employment_info_by_email(params={'email': login_data.username})

        response['name'] = user_data.name
        response['last_name'] = user_data.last_name
        response['email'] = user_data.email
        response['uuid'] = user_data.uuid

        return response

    async def get_employees_info(self, cpf: str) -> Employees:
        employees_date = await self.employees_repo.filter_by_with_address({'cpf': cpf})
        return employees_date

    async def get_employees_info_by_uuid(self, uuid: str) -> Employees:
        employees_date = await self.employees_repo.filter_by_with_address({'uuid': uuid})
        return employees_date

    async def get_all_employees(self, params: Dict):
        employees_list, total = await self.employees_repo.get_all_employees(params=params)
        return paginate(employees_list, params.get('offset'), total)
