from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    id: int
    display_name: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True
