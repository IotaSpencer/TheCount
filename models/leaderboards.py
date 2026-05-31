from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class Leaderboards(Base):
    __tablename__ = 'leaderboards'

    serverID: Mapped[Optional[str]] = mapped_column(String(64), name='serverID')
    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), default='')
    guildname: Mapped[Optional[str]] = mapped_column(String(255), default='')
    score: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"Leaderboards(channelID={self.channelID!r}, score={self.score})"