from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    nickname: str
    email: str
    phone: str
    password: str
    role: str
    country: str
    state: str
    city: str


class LoginForm(BaseModel):
    username: str
    password: str


class OperationCreateRequest(BaseModel):
    required_amount: float
    annual_interest: float
    deadline: date
    current_amount: float


class OperationUpdateRequest(BaseModel):
    operation_id: str


class BidRequest(BaseModel):
    operation_id: str
    invested_amount: float
    interest_rate: float