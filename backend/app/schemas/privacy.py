from pydantic import BaseModel, Field


class DeleteMyAccountRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    confirmation: str = Field(min_length=1, max_length=50)


class LegalAcceptanceRequest(BaseModel):
    terms_accepted: bool
    privacy_acknowledged: bool
