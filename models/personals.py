from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class Personals(Base):
    """Personal bests table for tracking how many each user can get right or wrong"""
    __tablename__ = 'personals'

    userID: Mapped[str] = mapped_column(String(64), primary_key=True)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"Personals(userID={self.userID!r}, correct_count={self.correct_count}, incorrect_count={self.incorrect_count})"