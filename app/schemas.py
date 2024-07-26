from pydantic import BaseModel

class TaskCreate(BaseModel):
    uuid: str
    status: str

class Task(BaseModel):
    id: int
    uuid: str
    status: str

    class Config:
        orm_mode = True

