from datetime import date, datetime
from typing import List
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import config

engine = create_async_engine(config.DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    operator_name: Mapped[str] = mapped_column(String(128), default="Maksym Khvorostenko", nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="uk", nullable=False)


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    operator_name: Mapped[str] = mapped_column(String(128), default="Maksym Khvorostenko", nullable=False)
    date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    shift_hours: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    robots: Mapped[List["RobotEntry"]] = relationship(
        "RobotEntry", back_populates="shift", cascade="all, delete-orphan", lazy="selectin"
    )


class RobotEntry(Base):
    __tablename__ = "robot_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False)
    machine: Mapped[str] = mapped_column(String(32), nullable=False)
    pallets_count: Mapped[float] = mapped_column(Float, nullable=False)
    cartons_left: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tonnage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    has_downtime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    downtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downtime_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    has_minor_incident: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    minor_incident_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    shift: Mapped["Shift"] = relationship("Shift", back_populates="robots")


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)