from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base


class Leaderboards(Base):
    __tablename__ = 'leaderboards'

    serverID: Mapped[str] = mapped_column(primary_key=True)
    score: Mapped[int] = mapped_column(Integer(100))

    def __repr__(self) -> str:
        return f"Leaderboards(serverID={self.serverID!r}, score={self.score})"