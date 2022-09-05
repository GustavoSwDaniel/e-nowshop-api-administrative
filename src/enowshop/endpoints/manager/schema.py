from datetime import datetime, date
from enum import Enum
from typing import List

from pycpfcnpj import cpfcnpj
from pydantic import BaseModel, Field, validator, root_validator


class PhoneTypes(Enum):
    CELL = 'Cell'
    TELEPHONE = 'Telephone'


class PhonesSchema(BaseModel):
    type: PhoneTypes
    number: str

    class Config:
        use_enum_values = True


class ManageRegisterSchema(BaseModel):
    name: str
    last_name: str
    email: str
    cpf: str
    position: str
    salary: int
    birth_date: str
    phones: List[PhonesSchema]
    password: str = Field(regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}')

    @validator('cpf')
    def cpf_validate(cls, data):
        if not cpfcnpj.validate(data):
            raise ValueError('Invalid CPF')

        return data

    @root_validator
    def convert_string_to_date(cls, values):
        values['birth_date'] = datetime.strptime(values.get('birth_date'), '%d-%m-%Y').date()
        return values


class ManagerLoginSchema(BaseModel):
    username: str
    password: str


class ManagerLoginResponseSchema(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str


class PhonesResponseSchema(PhonesSchema):
    class Config:
        orm_mode = True
        use_enum_values = True


class EmployeesDataSchema(BaseModel):
    uuid: str
    name: str
    last_name: str
    email: str
    cpf: str
    position: str
    admission_date: datetime
    created_at: datetime
    employees_phones: List[PhonesResponseSchema]

    class Config:
        orm_mode = True
        use_enum_values = True
