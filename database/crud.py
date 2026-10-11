from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# Імпортуй свою модель зміни (наприклад, Shift)
# from database.models import Shift 

async def get_recent_shifts(session: AsyncSession, user_id: int, days: int = 30):
    start_date = datetime.now() - timedelta(days=days)
    stmt = (
        select(Shift)
        .where(
            Shift.user_id == user_id,
            Shift.date >= start_date
        )
        .order_by(Shift.date.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()
from datetime import datetime, timedelta
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Shift


async def get_shifts_last_days(session: AsyncSession, user_id: int, days: int = 30) -> Sequence[Shift]:
    start_date = datetime.now() - timedelta(days=days)
    stmt = (
        select(Shift)
        .where(
            Shift.user_id == user_id,
            Shift.date >= start_date
        )
        .order_by(Shift.date.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()