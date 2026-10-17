from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class CarBaseSchema(BaseModel):
    vin_number: str = Field(..., min_lenght=17, max_lenght=17)
    reg_number: str = Field(..., min_lenght=6, max_lenght=8)
    brand: str = Field(..., min_lenght=2, max_lenght=50)
    model: str = Field(..., max_length=50)
    engine_volume: Optional[float] = Field(None, gt=0.0, lt=8.0)
    color: Optional[str]

class CarResponseSchema(CarBaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
