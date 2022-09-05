import os


class Config:
    BROKER_URL = os.getenv('BROKER_URL', 'localhost:9092')

    DATABASE_URL = os.getenv(
        'A-POSTGRES_DATABASE_URL', 'postgresql+asyncpg://enowshop:enowshop@127.0.0.1:5432/enowshop')

    KEYCLOAK_URL = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
    KEYCLOAK_REALMS = os.getenv('KEYCLOAK_REALMS', 'employees')
    KEYCLOAK_PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    KEYCLOAK_MANAGER_PUBLIC_KEY = os.getenv('KEYCLOAK_MANAGER_PUBLIC_KEY')
    KEYCLOAK_CLIENT_ID_ADMIN_CLI = os.getenv('KEYCLOAK_CLIENT_ID_ADMIN_CLI', 'admin-cli')
    KEYCLOAK_CLIENT_SECRET_ADMIN_CLI = str(os.getenv('KEYCLOAK_CLIENT_SECRET_ADMIN_CLI'))
    KEYCLOAK_CLIENT_SECRET_EMPLOYEES = str(os.getenv('KEYCLOAK_CLIENT_SECRET_EMPLOYEES'))
    KEYCLOAK_CLIENT_SECRET_MANAGER = str(os.getenv('KEYCLOAK_CLIENT_SECRET_MANAGER'))
    KEYCLOAK_CLIENT_ID_EMPLOYEES = os.getenv('KEYCLOAK_CLIENT_ID_EMPLOYEES', 'employees')
    KEYCLOAK_CLIENT_ID_MANAGER = os.getenv('KEYCLOAK_CLIENT_ID_MANAGER', 'manager')

