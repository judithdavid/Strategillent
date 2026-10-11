from pydantic import BaseModel, ConfigDict, Field


class OrganisationBase(BaseModel):
    name: str
    fictional: bool = True
    industry: str

    business_model: list[str] = Field(default_factory=list)
    markets: list[str] = Field(default_factory=list)

    customers: int | None = None
    employees: int | None = None

    products: list[str] = Field(default_factory=list)
    challenges: list[str] = Field(default_factory=list)

    goals: list[str] = Field(default_factory=list)
    processes: list[str] = Field(default_factory=list)
    technology: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)