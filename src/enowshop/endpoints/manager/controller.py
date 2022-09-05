from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, APIRouter, Request, status, Response, Depends

from enowshop.endpoints.dependecies import verify_manager, verify_cpf
from enowshop.endpoints.manager.schema import ManagerLoginResponseSchema, ManagerLoginSchema, \
    ManageRegisterSchema, EmployeesDataSchema
from enowshop.endpoints.manager.service import ManagerService
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post('/manager/auth', status_code=status.HTTP_200_OK, response_model=ManagerLoginResponseSchema)
@inject
async def login_employees(request: Request, login_data: ManagerLoginSchema,
                          manager_service: ManagerService = Depends(Provide(Container.manager_service))):
    response = await manager_service.login(login_data=login_data)
    return response


@router.post('/manager/employees', status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_manager)])
@inject
async def register_employees(request: Request, register_user_data: ManageRegisterSchema,
                             manager_service: ManagerService = Depends(Provide(Container.manager_service))):
    await manager_service.register_employees(register_user_data.dict())
    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/employees/{cpf}', status_code=status.HTTP_200_OK, response_model=EmployeesDataSchema,
            dependencies=[Depends(verify_manager), Depends(verify_cpf)])
@inject
async def get_employees_info(request: Request, cpf: str,
                             manager_service: ManagerService = Depends(Provide(Container.manager_service))):
    employees_data = await manager_service.get_employees_info(cpf=cpf)
    return employees_data


def configure(app: FastAPI):
    app.include_router(router)
