from pydantic import BaseModel, Field


class FavoriteCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=200)
    currency: str = Field(min_length=1, max_length=10)


class FavoriteStock(BaseModel):
    id: int
    user_id: int
    symbol: str
    name: str
    currency: str
    created_at: str
