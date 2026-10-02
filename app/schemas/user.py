# app/schemas/user.py
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):  # POST /auth/register
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)  # bcrypt only uses the first 72 bytes


class UserResponse(BaseModel):  # what the API sends back (never includes the password)
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)  # lets Pydantic read SQLAlchemy objects


class TokenResponse(BaseModel):  # what POST /auth/token sends back
    access_token: str
    token_type: str = "bearer"