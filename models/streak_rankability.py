from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class StreakRankability(Base):
    __tablename__ = 'streakrankability'

    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)
    rankable: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"StreakRankability(channelID={self.channelID!r}, rankable={self.rankable})"
