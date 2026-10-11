from datetime import date, timedelta
from typing import Any, Dict, List, Sequence, Tuple
from sqlalchemy import desc, extract, select
from database.models import RobotEntry, Shift, UserSettings, async_session

DEFAULT_OPERATOR_NAME = "Maksym Khvorostenko"
DEFAULT_LANGUAGE = "uk"


async def get_user_settings(user_id: int) -> Tuple[str, str]:
    async with async_session() as session:
        settings = await session.get(UserSettings, user_id)
        if settings:
            return settings.operator_name, settings.language
        return DEFAULT_OPERATOR_NAME, DEFAULT_LANGUAGE


async def set_user_operator_name(user_id: int, name: str) -> None:
    async with async_session() as session:
        settings = await session.get(UserSettings, user_id)
        if settings:
            settings.operator_name = name
        else:
            settings = UserSettings(user_id=user_id, operator_name=name, language=DEFAULT_LANGUAGE)
            session.add(settings)
        await session.commit()


async def set_user_language(user_id: int, lang: str) -> None:
    async with async_session() as session:
        settings = await session.get(UserSettings, user_id)
        if settings:
            settings.language = lang
        else:
            settings = UserSettings(user_id=user_id, operator_name=DEFAULT_OPERATOR_NAME, language=lang)
            session.add(settings)
        await session.commit()


async def save_complete_shift(
    user_id: int,
    shift_date: date,
    shift_hours: str,
    robots_data: List[Dict[str, Any]],
    operator_name: str,
) -> Shift:
    async with async_session() as session:
        new_shift = Shift(
            user_id=user_id,
            operator_name=operator_name,
            date=shift_date,
            shift_hours=shift_hours,
        )
        session.add(new_shift)
        await session.flush()

        for r in robots_data:
            entry = RobotEntry(
                shift_id=new_shift.id,
                machine=r["machine"],
                pallets_count=float(r["pallets_count"]),
                cartons_left=int(r.get("cartons_left", 0)),
                tonnage=float(r.get("tonnage", 0.0)),
                has_downtime=bool(r.get("has_downtime", False)),
                downtime_minutes=int(r.get("downtime_minutes", 0)),
                downtime_reason=r.get("downtime_reason"),
                has_minor_incident=bool(r.get("has_minor_incident", False)),
                minor_incident_note=r.get("minor_incident_note"),
            )
            session.add(entry)

        await session.commit()
        await session.refresh(new_shift)
        return new_shift


async def bulk_save_shifts(
    user_id: int,
    operator_name: str,
    shifts_payload: List[Dict[str, Any]],
) -> int:
    async with async_session() as session:
        async with session.begin():
            for s_data in shifts_payload:
                new_shift = Shift(
                    user_id=user_id,
                    operator_name=operator_name,
                    date=s_data["date"],
                    shift_hours=s_data["shift_hours"],
                )
                session.add(new_shift)
                await session.flush()

                for r in s_data["robots"]:
                    entry = RobotEntry(
                        shift_id=new_shift.id,
                        machine=r["machine"],
                        pallets_count=float(r["pallets_count"]),
                        cartons_left=int(r.get("cartons_left", 0)),
                        tonnage=float(r.get("tonnage", 0.0)),
                        has_downtime=bool(r.get("has_downtime", False)),
                        downtime_minutes=int(r.get("downtime_minutes", 0)),
                        downtime_reason=r.get("downtime_reason"),
                        has_minor_incident=False,
                        minor_incident_note=None,
                    )
                    session.add(entry)
        return len(shifts_payload)


async def get_user_shifts_for_period(user_id: int, days: int = 14) -> Sequence[Shift]:
    start_date = date.today() - timedelta(days=days)
    async with async_session() as session:
        stmt = (
            select(Shift)
            .where(Shift.user_id == user_id, Shift.date >= start_date)
            .order_by(Shift.date.asc(), Shift.id.asc())
        )
        result = await session.scalars(stmt)
        return result.all()


async def get_user_recent_shifts(user_id: int, limit: int = 7) -> Sequence[Shift]:
    async with async_session() as session:
        stmt = (
            select(Shift)
            .where(Shift.user_id == user_id)
            .order_by(desc(Shift.date), desc(Shift.id))
            .limit(limit)
        )
        result = await session.scalars(stmt)
        return result.all()


async def get_user_shifts_for_month(user_id: int, year: int, month: int) -> Sequence[Shift]:
    async with async_session() as session:
        stmt = (
            select(Shift)
            .where(
                Shift.user_id == user_id,
                extract("year", Shift.date) == year,
                extract("month", Shift.date) == month,
            )
            .order_by(Shift.date.asc(), Shift.id.asc())
        )
        result = await session.scalars(stmt)
        return result.all()


async def get_all_user_shifts(user_id: int) -> Sequence[Shift]:
    async with async_session() as session:
        stmt = (
            select(Shift)
            .where(Shift.user_id == user_id)
            .order_by(desc(Shift.date), desc(Shift.id))
        )
        result = await session.scalars(stmt)
        return result.all()