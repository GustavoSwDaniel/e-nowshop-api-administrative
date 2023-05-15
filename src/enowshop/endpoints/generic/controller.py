from dependency_injector.wiring import inject, Provide
from enowshop.endpoints.generic.schema import LogoutSchema
from config import Config
from enowshop.endpoints.dependecies import verify_jwt
from fastapi import APIRouter, FastAPI, status, Request, Depends

from enowshop.endpoints.generic.service import GenericService
from enowshop.infrastructure.containers import Container

router = APIRouter()


@router.post('/logout/{realm}', status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[Depends(verify_jwt)])
@inject
async def logout(request: Request, realm: str, refresh_token: LogoutSchema,
                 generic_service: GenericService = Depends(Provide(Container.generic_service))):
    token = request.headers['Authorization'].split(' ')[1]
    response = await generic_service.logout(token=token, 
                                            refresh_token=refresh_token.refresh_token,
                                            realm=realm)


def configure(app: FastAPI):
    app.include_router(router)
