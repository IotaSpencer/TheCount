from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base


class Personals(Base):
    """Personal bests table for tracking how many each user can get right or wrong"""
    __table__ = Table(
        'personals',
        Base.metadata,
        autoload_with=engine
    )
    __tablename__ = 'personals'

    userID: Mapped[str] = mapped_column(primary_key=True)
    correct_count: Mapped[int] = mapped_column(Integer(100))
    incorrect_count: Mapped[int] = mapped_column(Integer(100))

    # level 1: 20
    # level 2: 50
    # level 3: 100
    # level 4: 250
    # level 5: 500
    # level 6: 1000
    # level 7: 2500
    # level 8: 5000
    # level 9: 10000
    # level 10: 25000
    # level 11: 50000

    def __repr__(self) -> str:
        return f"Personals(serverID={self.userID!r}, correct_count={self.correct_count}, incorrect_count={self.incorrect_count})"