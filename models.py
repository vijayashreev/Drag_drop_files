from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)
    tag = Column(String, nullable=True)
    uploaded_by = Column(String, nullable=False)
    date_uploaded = Column(DateTime, default=datetime.utcnow)
