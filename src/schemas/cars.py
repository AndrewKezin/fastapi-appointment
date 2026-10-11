from pydantic import BaseModel, Field, UUID4

class SCarAdd(BaseModel):
    vin_number: str = Field(..., min_lenght=17, max_lenght=17)
    reg_number: str = Field(..., min_lenght=6, max_lenght=8)
    brand: str = Field(..., min_lenght=2, max_lenght=50)
    model: str = Field(..., max_length=50)
    engine_volume: float = Field(..., gt=0.0, lt=8.0) | None
    color: str | None

class SCar(SCarAdd):
    id: UUID4
