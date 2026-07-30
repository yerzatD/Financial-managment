from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    price: float
    image_url: str
    stock: int
    created_at: datetime