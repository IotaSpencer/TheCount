from typing import Optional
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class Channels(Base):
    __tablename__ = 'channels'

    serverID: Mapped[str] = mapped_column(String(64))
    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)
    current_count: Mapped[int] = mapped_column(Integer)
    last_userID: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    times_counted: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"Channels(serverID={self.serverID!r}, channelID={self.channelID}, current_count={self.current_count})"
