from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer, Table
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base, engine


class HighScores(Base):
    __table__ = Table(
        'highscores',
        Base.metadata,
        autoload_with=engine
    )
    serverID: Mapped[str] = mapped_column(String(64))
    channelID: Mapped[str] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(Integer())
    def __repr__(self) -> str:
        return f"HighScores(serverID={self.serverID!r}, score={self.score})"

# class HighScores(Base):
#     __tablename__ = 'highscores'
#
#     serverID: Mapped[str] = mapped_column(primary_key=True)
#     score: Mapped[int] = mapped_column(Integer(100))
#
#     def __repr__(self) -> str:
#         return f"HighScores(serverID={self.serverID!r}, score={self.score})"