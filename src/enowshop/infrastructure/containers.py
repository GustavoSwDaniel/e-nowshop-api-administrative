from dependency_injector import containers, providers
from enowshop.endpoints.employees.repository import EmployeesRepository, EmployeesPhonesRepository

from config import Config
from enowshop.domain.keycloak.keycloak import KeycloakService
from enowshop.endpoints.employees.service import EmployeesService
from enowshop.endpoints.manager.service import ManagerService
from enowshop.infrastructure.database.database_sql import PostgresDatabase


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    postgres_db = providers.Singleton(PostgresDatabase, database_url=Config.DATABASE_URL)

    # repository
    employees_repository = providers.Factory(EmployeesRepository, session_factory=postgres_db.provided.session)
    employees_phones_repository = providers.Factory(EmployeesPhonesRepository,
                                                    session_factory=postgres_db.provided.session)

    # services
    keycloak_service = providers.Factory(KeycloakService, client_id_admin_cli=Config.KEYCLOAK_CLIENT_ID_ADMIN_CLI,
                                         client_id=Config.KEYCLOAK_CLIENT_ID_EMPLOYEES,
                                         client_secret_admin_cli=Config.KEYCLOAK_CLIENT_SECRET_ADMIN_CLI,
                                         client_secret=Config.KEYCLOAK_CLIENT_SECRET_EMPLOYEES,
                                         keycloak_url=Config.KEYCLOAK_URL, realm=Config.KEYCLOAK_REALMS,
                                         client_id_manager=Config.KEYCLOAK_CLIENT_ID_MANAGER,
                                         client_secret_manager=Config.KEYCLOAK_CLIENT_SECRET_MANAGER)
    employees_services = providers.Factory(EmployeesService, employees_repository=employees_repository,
                                           employees_phones_repository=employees_phones_repository,
                                           keycloak_service=keycloak_service)
    manager_service = providers.Factory(ManagerService, employees_repository=employees_repository,
                                        employees_phones_repository=employees_phones_repository,
                                        keycloak_service=keycloak_service)
