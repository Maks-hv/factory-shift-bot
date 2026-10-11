from datetime import date
import re
from typing import Any, Dict, List
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.requests import bulk_save_shifts, get_user_settings

import_router = Router()

ROBOT_ENTRY_REGEX = re.compile(
    r"(?P<robot>[A-Za-z0-9А-Яа-я]+)\s*:\s*(?P<pallets>\d+(?:[.,]\d+)?)(?:\s*\((?P<cartons>\d+)\s*(?:krt|кор)?\))?",
    re.IGNORECASE,
)


@import_router.message(Command("import"))
async def cmd_bulk_import(message: Message) -> None:
    text_content = message.text.replace("/import", "").strip()

    if not text_content:
        await message.answer(
            "📋 <b>Швидкий пакетний імпорт змін</b>\n\n"
            "Надішліть команду разом із рядками у форматі:\n"
            "<code>/import\n"
            "16.09 | 1 | K13: 4.5 | K2: 8\n"
            "18.09 | 2 | K2: 8.5 | K13: 0 (28 krt)</code>\n\n"
            "Формат: <code>ДД.ММ | Зміна(1/2/3) | Робот: Палети (опц. коробки)</code>",
            parse_mode="HTML",
        )
        return

    operator_name, _ = await get_user_settings(message.from_user.id)
    lines = [line.strip() for line in text_content.split("\n") if line.strip()]

    parsed_shifts: List[Dict[str, Any]] = []
    errors: List[str] = []
    current_year = date.today().year

    shift_hours_map = {
        "1": "07:00-15:00",
        "2": "15:00-23:00",
        "3": "23:00-07:00",
    }

    for idx, line in enumerate(lines, 1):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            errors.append(f"Рядок {idx}: недостатньо розділювачів '|'")
            continue

        date_str, shift_code = parts[0], parts[1]
        robots_parts = parts[2:]

        try:
            day, month = map(int, date_str.split("."))
            shift_date = date(current_year, month, day)
        except Exception:
            errors.append(f"Рядок {idx}: помилка дати '{date_str}'")
            continue

        hours = shift_hours_map.get(shift_code, shift_code)
        robots_list: List[Dict[str, Any]] = []

        for r_str in robots_parts:
            match = ROBOT_ENTRY_REGEX.search(r_str)
            if not match:
                continue

            r_name = match.group("robot").upper()
            pal_val = float(match.group("pallets").replace(",", "."))
            cartons_val = int(match.group("cartons")) if match.group("cartons") else 0

            robots_list.append({
                "machine": r_name,
                "pallets_count": pal_val,
                "cartons_left": cartons_val,
                "tonnage": 0.0,
                "has_downtime": False,
                "downtime_minutes": 0,
                "downtime_reason": "Brak produktu" if pal_val == 0 and cartons_val == 0 else None,
            })

        if not robots_list:
            errors.append(f"Рядок {idx}: не знайдено записів роботів")
            continue

        parsed_shifts.append({
            "date": shift_date,
            "shift_hours": hours,
            "robots": robots_list,
        })

    if not parsed_shifts:
        await message.answer(f"❌ Не вдалося розпізнати жодної зміни.\nПомилки:\n" + "\n".join(errors[:5]))
        return

    imported_count = await bulk_save_shifts(
        user_id=message.from_user.id,
        operator_name=operator_name,
        shifts_payload=parsed_shifts,
    )

    result_msg = f"✅ <b>Успішно імпортовано {imported_count} змін!</b>"
    if errors:
        result_msg += f"\n\n⚠️ Пропущено рядків із помилками: {len(errors)}"

    await message.answer(result_msg, parse_mode="HTML")