from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Setting(Base):
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)