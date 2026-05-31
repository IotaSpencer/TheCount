from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class HighScores(Base):
    __tablename__ = 'highscores'

    serverID: Mapped[str] = mapped_column(String(64))
    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"HighScores(serverID={self.serverID!r}, channelID={self.channelID!r}, score={self.score})"