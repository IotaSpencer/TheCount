from typing import Optional
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.base import Base


class Settings(Base):
    __tablename__ = 'settings'

    channelID: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Map model attributes to the existing snake_case DB column names
    Step: Mapped[float] = mapped_column(Float, name='step', default=1)
    StartingNumber: Mapped[float] = mapped_column(Float, name='starting_number', default=0)

    EnableWolframAlpha: Mapped[int] = mapped_column(Integer, name='enable_wa', default=0)
    EnableBinary: Mapped[int] = mapped_column(Integer, name='enable_binary', default=1)
    EnableExpressions: Mapped[int] = mapped_column(Integer, name='enable_expr', default=1)
    RoundAllGuesses: Mapped[int] = mapped_column(Integer, name='round_guesses', default=0)
    AllowSingleUserCount: Mapped[int] = mapped_column(Integer, name='enable_single_user_count', default=0)
    ForceIntegerConversions: Mapped[int] = mapped_column(Integer, name='force_integer', default=1)

    def __repr__(self) -> str:
        return f"Settings(channelID={self.channelID})"
