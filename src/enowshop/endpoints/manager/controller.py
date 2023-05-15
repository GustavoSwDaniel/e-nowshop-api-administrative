from config import Config
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, APIRouter, Request, status, Response, Depends

from enowshop.endpoints.dependecies import verify_jwt, verify_manager, verify_cpf, verify_role
from enowshop.endpoints.manager.schema import ManagerLoginResponseSchema, ManagerLoginSchema, \
    ManageRegisterSchema, EmployeesDataSchema, PaginateEmployeeListSchema
from enowshop.endpoints.manager.service import ManagerService
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post('/manager/auth', status_code=status.HTTP_200_OK, response_model=ManagerLoginResponseSchema)
@inject
async def login_employees(request: Request, login_data: ManagerLoginSchema,
                          manager_service: ManagerService = Depends(Provide(Container.manager_service))):
    print(login_data)
    response = await manager_service.login(login_data=login_data)
    return response


@router.post('/manager/employees', status_code=status.HTTP_201_CREATED)
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


@router.get('/manager/employees', status_code=status.HTTP_200_OK, response_model=PaginateEmployeeListSchema)
@inject
async def get_employee_list(request: Request,
                            dependencies=[Depends(verify_manager)],
                            manager_service: ManagerService = Depends(Provide[Container.manager_service])):
    params = request.query_params
    params = {
        'limit': int(params.get('limit', 12)),
        'offset': int(params.get('offset', 0)),
        'order_by': params.get('order_by', None)
    }
    employees_list = await manager_service.get_all_employees(params=params)
    return employees_list


@router.get('/employee/{uuid}', status_code=status.HTTP_200_OK, response_model=EmployeesDataSchema,
            dependencies=[Depends(verify_role)])
@inject
async def get_employees_info_by_uuid(request: Request, uuid: str,
                                     manager_service: ManagerService = Depends(Provide(Container.manager_service))):
    employees_data = await manager_service.get_employees_info_by_uuid(uuid=uuid)
    return employees_data


def configure(app: FastAPI):
    app.include_router(router)
