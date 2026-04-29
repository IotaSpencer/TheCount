from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer, Table
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base, engine


class Settings(Base):
    __table__ = Table(
        'settings',
        Base.metadata,
        autoload_with=engine
    )
    __tablename__ = 'settings'

    serverID: Mapped[str] = mapped_column(String(64))
    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)
    current_count: Mapped[int] = mapped_column(Integer(100))
    def __repr__(self) -> str:
        return f"Settings(serverID={self.serverID!r}, channelID={self.channelID}, current_count={self.current_count})"
