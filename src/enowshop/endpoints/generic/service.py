from enowshop.domain.keycloak.keycloak import KeycloakService
from config import Config


class GenericService:
    def __init__(self, keycloak_service: KeycloakService):
        self.keycloak_service = keycloak_service
    
    def get_credentials(self, realm: str):
        credentials = {
            'manager': {'client_id': Config.KEYCLOAK_CLIENT_ID_MANAGER, 'client_secret': Config.KEYCLOAK_CLIENT_SECRET_MANAGER},
            'employees': {'client_id': Config.KEYCLOAK_CLIENT_ID_EMPLOYEES, 'client_secret': Config.KEYCLOAK_CLIENT_SECRET_EMPLOYEES}   
        }
        return credentials[realm]

    async def logout(self, token: str, refresh_token: str,realm: str):
        credentials = self.get_credentials(realm)
        await self.keycloak_service.logout(token=token, refresh_token=refresh_token, client_id=credentials['client_id'], 
                                           client_secret=credentials['client_secret'],
                                           realm=realm)
