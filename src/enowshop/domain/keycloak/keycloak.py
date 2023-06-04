import logging
from re import sub
from typing import Dict, Union

import httpx

from exception import KeyCloakException, KeycloakPasswordException


class KeycloakService:
    def __init__(self, keycloak_url: str, realm: str,
                 client_secret: str = None, client_secret_admin_cli: str = None, client_id: str = None,
                 client_id_admin_cli: str = None, client_id_manager: str = None, client_secret_manager: str = None):
        self.__client_id = client_id
        self.__client_id_admin_cli = client_id_admin_cli
        self.__keycloak_url = keycloak_url
        self.__realm = realm
        self.__client_secret_admin_cli = client_secret_admin_cli
        self.__client_secret_manager = client_secret_manager
        self.__client_secret = client_secret
        self.__headers = {'headers': {'Content-Type': 'application/x-www-form-urlencoded'}}
        self.__client_id_manager = client_id_manager
        self.logger = logging.getLogger(__name__)

    def __build_payload_to_create_user(self, data: Dict, password: str, employee_id: int):
        self.logger.info('[KeycloakService] - Creating payload to create user ')
        return {
            "firstName": data.get('name'),
            "lastName": data.get('last_name'),
            "attributes": {
                "employees_id": employee_id
            },
            "groups": [],
            "email": data.get('email'),
            "enabled": "true",
            "username": data.get('email'),
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False
                }
            ]
        }

    def __build_payload_to_authorization(self, payload_type: str, username: str = None, password: str = None) -> Dict:
        self.logger.info('[KeycloakService] - Creating payload to auth admin keycloak')
        payload = {'admin-cli': {'client_id': self.__client_id_admin_cli,
                                 'grant_type': 'client_credentials', 'client_secret': self.__client_secret_admin_cli},
                   'default_user': {'client_id': self.__client_id, 'username': username, 'password': password,
                                    'grant_type': 'password', 'client_secret': self.__client_secret},
                   'admin_user': {'client_id': self.__client_id_admin_cli, 'username': 'admin', 'password': 'admin',
                                  'grant_type': 'password'}
                   }
        return payload[payload_type]

    async def __auth_admin_cli_client(self) -> Dict:
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/{self.__realm}/protocol/openid-connect/token',
                data=self.__build_payload_to_authorization('admin-cli'))

        if response.status_code != httpx.codes.OK:
            raise Exception(f'Admin-cli not authorized')

        return response.json()

    async def auth_user(self, username: str, password: str) -> Dict:
        async with httpx.AsyncClient(**self.__headers) as client:
            print(self.__realm)
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/{self.__realm}/protocol/openid-connect/token',
                data=self.__build_payload_to_authorization(payload_type='default_user', username=username,
                                                           password=password)
            )
            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise KeyCloakException('User does not authorized')
            if response.status_code != httpx.codes.OK:
                raise KeyCloakException('Error during login')

        return response.json()

    async def auth_user_admin(self) -> Dict:
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/master/protocol/openid-connect/token',
                data=self.__build_payload_to_authorization(payload_type='admin_user')
            )

            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise KeyCloakException('User does not authorized')
            if response.status_code != httpx.codes.OK:
                raise KeyCloakException('Error during login')

        return response.json()

    @staticmethod
    def _get_uuid_keycloak(response: httpx.Response) -> str:
        return response.headers.raw[1][1].decode('utf-8').split('/')[-1]

    async def create_user_by_admin_cli(self, data: Dict, password: str, employee_id: int) -> Union[str, None]:
        authorization = await self.__auth_admin_cli_client()

        payload_create_user = self.__build_payload_to_create_user(data=data, password=password, employee_id=employee_id)
        self.__headers['headers']['Content-Type'] = 'application/json'
        self.__headers['headers']['Authorization'] = f"{authorization['token_type']} {authorization['access_token']}"
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/admin/realms/{self.__realm}/users',
                json=payload_create_user
            )
        if response.status_code != httpx.codes.CREATED:
            raise KeyCloakException(f'Error register in keycloak. Error: {response.json()}')

        return self._get_uuid_keycloak(response=response)

    def _build_payload_to_update_user_data(self, update_data):
        return {
            "attributes": self.__convert_update_user_data(update_data=update_data)
        }

    @staticmethod
    def __convert_update_user_data(update_data: Dict) -> Dict:
        converted_data = {}
        if update_data.get('name'):
            converted_data['firstName'] = update_data.get('name')
        if update_data.get('last_name'):
            converted_data['lastName'] = update_data.get('last_name')
        return converted_data

    async def update_user_data(self, uuid_user: str, update_data: dict):
        update_data = self._build_payload_to_update_user_data(update_data=update_data)
        authorization = await self.auth_user_admin()

        self.__headers['headers']['Content-Type'] = 'application/json'
        self.__headers['headers']['Authorization'] = f"{authorization['token_type']} {authorization['access_token']}"

        async with httpx.AsyncClient(**self.__headers) as client:
            await client.put(
                f'{self.__keycloak_url}/auth/admin/realms/users/users/{uuid_user}',
                json=update_data
            )

    @staticmethod
    def __camel_case(key):
        key = sub(r"(_|-)+", " ", key).title().replace(" ", "")

    async def check_old_password(self, username: str, password: str) -> Dict:
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/{self.__realm}/protocol/openid-connect/token',
                data=self.__build_payload_to_authorization(payload_type='default_user', username=username,
                                                           password=password)
            )
            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise KeycloakPasswordException('User does not authorized')
            if response.status_code != httpx.codes.OK:
                raise KeyCloakException('Error during check old password')

        return response.json()

    @staticmethod
    def __build_payload_to_update_password(new_password: str):
        return {
            "type": "password",
            "value": new_password,
            "temporary": False
        }

    async def change_password(self, email: str, keycloak_user_id: str, update_password: Dict,
                              recovery_mode: bool = False):
        if not recovery_mode:
            await self.check_old_password(username=email, password=update_password.get('current_password'))

        response_auth = await self.auth_user_admin()

        self.__headers['headers']['Content-Type'] = 'application/json'
        self.__headers['headers']['Authorization'] = f"{response_auth['token_type']} {response_auth['access_token']}" \

        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.put(
                f'{self.__keycloak_url}/auth/admin/realms/users/users/{keycloak_user_id}/reset-password',
                json=self.__build_payload_to_update_password(new_password=update_password.get('new_password'))
            )

    def __build_payload_login_manager(self, username: str, password: str):
        return {'client_id': self.__client_id_manager, 'username': username, 'password': password,
                'client_secret': self.__client_secret_manager,
                'grant_type': 'password'}

    async def auth_manager(self, username: str, password: str) -> Dict:
        async with httpx.AsyncClient(**self.__headers) as client:
            print(self.__client_secret_manager)
            data = self.__build_payload_login_manager(username=username, password=password)
            print(data)
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/manager/protocol/openid-connect/token',
                data=data
            )
            if response.status_code == httpx.codes.UNAUTHORIZED:
                raise KeyCloakException('User does not authorized')
            if response.status_code != httpx.codes.OK:
                raise KeyCloakException('Error during login')

        return response.json()

    async def revoke_token(self, token: str, client_id: str, client_secret: str, realm: str):
        print(f'{self.__keycloak_url}/auth/realms/{realm}/protocol/openid-connect/revoke')
        print(token)
        print(client_id)
        print(client_secret)
        print(realm)
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/{realm}/protocol/openid-connect/revoke',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'token': token
                }
            )
            print(response.status_code)
            if response.status_code != httpx.codes.OK:
                raise KeyCloakException('Error during revoke token')
            
    async def close_session(self, refresh_token: str, client_id: str, client_secret: str, realm: str):
        async with httpx.AsyncClient(**self.__headers) as client:
            response = await client.post(
                f'{self.__keycloak_url}/auth/realms/{realm}/protocol/openid-connect/logout',
                data={
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'refresh_token': refresh_token
                }
            )
            print(response.status_code)
            if response.status_code != httpx.codes.NO_CONTENT:
                raise KeyCloakException('Error during logout')

    async def logout(self, refresh_token: str, token: str, client_id: str, client_secret: str, realm: str):
        await self.revoke_token(token=token, client_id=client_id, client_secret=client_secret, realm=realm)
        await self.close_session(refresh_token=refresh_token, client_id=client_id, client_secret=client_secret, realm=realm)