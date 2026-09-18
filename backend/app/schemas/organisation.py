from pydantic import BaseModel, ConfigDict


class OrganisationBase(BaseModel):
    name: str
    fictional: bool = True
    industry: str
    business_model: list[str] = []
    markets: list[str] = []
    customers: int | None = None
    employees: int | None = None
    products: list[str] = []
    challenges: list[str] = []


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )