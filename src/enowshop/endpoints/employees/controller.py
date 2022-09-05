from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, FastAPI, status, Request, Depends

from enowshop.endpoints.employees.schema import LoginSchema, LoginResponseSchema
from enowshop.endpoints.employees.service import EmployeesService
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post('/employees/auth', status_code=status.HTTP_200_OK, response_model=LoginResponseSchema)
@inject
async def login_employees(request: Request, login_data: LoginSchema,
                          users_employees: EmployeesService = Depends(Provide(Container.employees_services))):
    response = await users_employees.login(login_data=login_data)
    return response


def configure(app: FastAPI):
    app.include_router(router)
