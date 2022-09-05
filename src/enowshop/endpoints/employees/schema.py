from datetime import datetime
from enum import Enum
from typing import Union, List, Dict, Optional

from enowshop_models.models.users_address import State
from pycpfcnpj import cpfcnpj
from pydantic import BaseModel, validator, Field


class LoginSchema(BaseModel):
    username: str
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: str


class PhoneTypes(Enum):
    CELL = 'Cell'
    TELEPHONE = 'Telephone'


class PhonesSchema(BaseModel):
    type: PhoneTypes
    number: str

    class Config:
        use_enum_values = True


class AddressResponseSchema(BaseModel):
    id: int
    street: str
    cep: str
    city: str
    state: State
    village: str
    complement: Union[str, None]

    class Config:
        orm_mode = True
        use_enum_values = True


class PhonesResponseSchema(PhonesSchema):
    class Config:
        orm_mode = True
        use_enum_values = True


class UserDataSchema(BaseModel):
    name: str
    last_name: str
    email: str
    cpf: str
    user_phones: List[PhonesResponseSchema]
    user_address: List[AddressResponseSchema]

    class Config:
        orm_mode = True
        use_enum_values = True


class UpdateUserData(BaseModel):
    name: Optional[str]
    last_name: Optional[str]


class UpdateUserAddressSchema(BaseModel):
    street: Optional[str]
    cep: Optional[str]
    city: Optional[str]
    state: Optional[State]
    village: Optional[str]
    complement: Optional[str]


class UpdateUserPhoneSchema(BaseModel):
    type: PhoneTypes
    number: str

    class Config:
        use_enum_values = True


class UpdatePasswordsSchema(BaseModel):
    current_password: str
    new_password: str = Field(regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}')
    confirmation: str

    @validator('confirmation')
    def passwords_match(cls, confirmation, values, **kwargs):
        if 'new_password' in values and confirmation != values['new_password']:
            raise ValueError('passwords do not match')
        return confirmation


class RecoveryPasswordsSchema(BaseModel):
    new_password: str = Field(regex='^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}')
    confirmation: str

    @validator('confirmation')
    def passwords_match(cls, confirmation, values, **kwargs):
        if 'new_password' in values and confirmation != values['new_password']:
            raise ValueError('passwords do not match')
        return confirmation


class EmailRecoveryPassword(BaseModel):
    email: str
