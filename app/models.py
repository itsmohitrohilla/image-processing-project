from sqlalchemy import Column, String, Integer
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True)
    status = Column(String)
    output_csv_path = Column(String)