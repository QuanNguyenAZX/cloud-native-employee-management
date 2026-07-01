from sqlmodel import Field, SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
    token_type: str | None = None
    jti: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(SQLModel):
    refresh_token: str = Field(min_length=1)
