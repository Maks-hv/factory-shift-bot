from datetime import datetime
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.requests import (
    get_user_recent_shifts,
    get_shift_by_id,
    delete_shift_by_id,
    update_shift_date,
    update_shift_hours,
    update_shift_pallets,
    update_shift_downtime,
)

router = Router()


class EditShiftFSM(StatesGroup):
    waiting_for_date = State()
    waiting_for_pallets = State()
    waiting_for_downtime = State()


def get_shift_pallets(shift_obj) -> float:
    robots = getattr(shift_obj, "robots", []) or []
    total = 0.0
    for r in robots:
        for field in ("pallets", "pallets_count", "pallet_count", "count"):
            val = getattr(r, field, None)
            if val is not None:
                try:
                    total += float(val)
                    break
                except (ValueError, TypeError):
                    continue
    return total


def get_shift_downtime(shift_obj) -> int:
    robots = getattr(shift_obj, "robots", []) or []
    total = 0
    for r in robots:
        for field in ("downtime_minutes", "downtime", "downtime_mins"):
            val = getattr(r, field, None)
            if val is not None:
                try:
                    total += int(val)
                    break
                except (ValueError, TypeError):
                    continue
    return total


def get_shift_tag(shift_hours: str) -> str:
    raw = str(shift_hours or "").strip()
    if "15" in raw or raw.startswith("2"):
        return "2 зм"
    elif "23" in raw or raw.startswith("3"):
        return "3 зм"
    elif "07" in raw or "7" in raw or raw.startswith("1"):
        return "1 зм"
    return "2 зм" if raw else "—"


@router.message(Command("history"))
@router.message(F.text.in_({"📋 Останні 30 днів", "📋 Ostatnie 30 dni", "📋 Last 30 days"}))
async def show_shifts_history(message: types.Message):
    shifts = await get_user_recent_shifts(user_id=message.from_user.id, limit=30)

    if not shifts:
        await message.answer(
            "📭 За останні 30 днів записів не знайдено.",
            parse_mode=ParseMode.HTML,
        )
        return

    total_pallets = sum(get_shift_pallets(s) for s in shifts)
    total_downtime = sum(get_shift_downtime(s) for s in shifts)

    lines = [
        "📊 <b>Зведення за останні 30 днів:</b>",
        f"▫️ Змін: <b>{len(shifts)}</b>",
        f"▫️ Всього палет: <b>{total_pallets:g} шт.</b>",
        f"▫️ Простій: <b>{total_downtime} хв</b>\n",
        "<code>Дата   | Зміна  | Палети </code>",
        "<code>--------------------------</code>",
    ]

    for s in shifts:
        date_str = s.date.strftime("%d.%m") if hasattr(s.date, "strftime") else str(s.date)[5:10]
        shift_tag = get_shift_tag(getattr(s, "shift_hours", ""))
        p_val = get_shift_pallets(s)
        pallets_str = f"{p_val:g}"
        lines.append(f"<code>{date_str:<6} | {shift_tag:^6} | {pallets_str:>4} шт.</code>")

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редагувати зміну", callback_data="history:pick_edit")]
        ]
    )

    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=kb)


@router.callback_query(F.data == "history:pick_edit")
async def pick_shift_to_edit(callback: types.CallbackQuery):
    shifts = await get_user_recent_shifts(user_id=callback.from_user.id, limit=10)

    if not shifts:
        await callback.answer("Немає доступних змін для редагування.", show_alert=True)
        return

    buttons = []
    for s in shifts:
        date_str = s.date.strftime("%d.%m") if hasattr(s.date, "strftime") else str(s.date)[5:10]
        p_val = get_shift_pallets(s)
        shift_tag = get_shift_tag(getattr(s, "shift_hours", ""))
        btn_text = f"📅 {date_str} ({shift_tag}, {p_val:g} пал.)"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"shift_manage:{s.id}")])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="history:close_edit")])

    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@router.callback_query(F.data == "history:close_edit")
async def close_edit_menu(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редагувати зміну", callback_data="history:pick_edit")]
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


# Головне меню управління конкретною зміною
@router.callback_query(F.data.startswith("shift_manage:"))
async def manage_single_shift(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    shift_id = int(callback.data.split(":")[1])
    shift = await get_shift_by_id(shift_id)

    if not shift:
        await callback.answer("Зміну не знайдено або вже видалено.", show_alert=True)
        return

    date_str = shift.date.strftime("%d.%m.%Y") if hasattr(shift.date, "strftime") else str(shift.date)[:10]
    shift_tag = get_shift_tag(shift.shift_hours)
    pallets = get_shift_pallets(shift)
    downtime = get_shift_downtime(shift)

    text = (
        f"⚙️ <b>Редагування зміни</b>\n\n"
        f"📅 <b>Дата:</b> {date_str}\n"
        f"🕒 <b>Зміна/Години:</b> {shift_tag} ({shift.shift_hours})\n"
        f"📦 <b>Палети:</b> {pallets:g} шт.\n"
        f"⏱ <b>Простій:</b> {downtime} хв\n\n"
        f"<i>Оберіть, що саме ви хочете змінити:</i>"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Змінити дату", callback_data=f"edit_field:date:{shift_id}")],
            [
                InlineKeyboardButton(text="🕒 1 зм (07-15)", callback_data=f"set_shift_time:{shift_id}:07:00-15:00"),
                InlineKeyboardButton(text="🕒 2 зм (15-23)", callback_data=f"set_shift_time:{shift_id}:15:00-23:00"),
                InlineKeyboardButton(text="🕒 3 зм (23-07)", callback_data=f"set_shift_time:{shift_id}:23:00-07:00"),
            ],
            [
                InlineKeyboardButton(text="📦 Змінити палети", callback_data=f"edit_field:pallets:{shift_id}"),
                InlineKeyboardButton(text="⏱ Змінити простій", callback_data=f"edit_field:downtime:{shift_id}"),
            ],
            [InlineKeyboardButton(text="🗑 ВИДАЛИТИ ЗМІНУ", callback_data=f"shift_delete_confirm:{shift_id}")],
            [InlineKeyboardButton(text="◀️ До списку змін", callback_data="history:pick_edit")],
        ]
    )

    await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    await callback.answer()


# Швидка зміна годин/номера зміни через кнопки
# Швидка зміна годин/номера зміни через кнопки
@router.callback_query(F.data.startswith("set_shift_time:"))
async def change_shift_time(callback: types.CallbackQuery, state: FSMContext):
    _, shift_id_str, new_time = callback.data.split(":", 2)
    shift_id = int(shift_id_str)
    await update_shift_hours(shift_id, new_time)
    await callback.answer(f"Зміну оновлено: {new_time}!", show_alert=False)

    shift = await get_shift_by_id(shift_id)
    if not shift:
        return

    date_str = shift.date.strftime("%d.%m.%Y") if hasattr(shift.date, "strftime") else str(shift.date)[:10]
    shift_tag = get_shift_tag(shift.shift_hours)
    pallets = get_shift_pallets(shift)
    downtime = get_shift_downtime(shift)

    text = (
        f"⚙️ <b>Редагування зміни</b>\n\n"
        f"📅 <b>Дата:</b> {date_str}\n"
        f"🕒 <b>Зміна/Години:</b> {shift_tag} ({shift.shift_hours})\n"
        f"📦 <b>Палети:</b> {pallets:g} шт.\n"
        f"⏱ <b>Простій:</b> {downtime} хв\n\n"
        f"<i>Оберіть, що саме ви хочете змінити:</i>"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Змінити дату", callback_data=f"edit_field:date:{shift_id}")],
            [
                InlineKeyboardButton(text="🕒 1 зм (07-15)", callback_data=f"set_shift_time:{shift_id}:07:00-15:00"),
                InlineKeyboardButton(text="🕒 2 зм (15-23)", callback_data=f"set_shift_time:{shift_id}:15:00-23:00"),
                InlineKeyboardButton(text="🕒 3 зм (23-07)", callback_data=f"set_shift_time:{shift_id}:23:00-07:00"),
            ],
            [
                InlineKeyboardButton(text="📦 Змінити палети", callback_data=f"edit_field:pallets:{shift_id}"),
                InlineKeyboardButton(text="⏱ Змінити простій", callback_data=f"edit_field:downtime:{shift_id}"),
            ],
            [InlineKeyboardButton(text="🗑 ВИДАЛИТИ ЗМІНУ", callback_data=f"shift_delete_confirm:{shift_id}")],
            [InlineKeyboardButton(text="◀️ До списку змін", callback_data="history:pick_edit")],
        ]
    )

    await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# Видалення
@router.callback_query(F.data.startswith("shift_delete_confirm:"))
async def confirm_delete_shift(callback: types.CallbackQuery):
    shift_id = int(callback.data.split(":")[1])
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚠️ ТАК, ВИДАЛИТИ", callback_data=f"shift_delete_do:{shift_id}")],
            [InlineKeyboardButton(text="Скасувати", callback_data=f"shift_manage:{shift_id}")],
        ]
    )
    await callback.message.edit_text("Ви впевнені, що хочете безповоротно видалити цю зміну?", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("shift_delete_do:"))
async def execute_delete_shift(callback: types.CallbackQuery):
    shift_id = int(callback.data.split(":")[1])
    await delete_shift_by_id(shift_id)
    await callback.answer("Зміну успішно видалено!", show_alert=True)
    await pick_shift_to_edit(callback)


# Старт FSM для введення значень
@router.callback_query(F.data.startswith("edit_field:"))
async def prompt_edit_field(callback: types.CallbackQuery, state: FSMContext):
    _, field, shift_id = callback.data.split(":")
    await state.update_data(shift_id=int(shift_id))

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Скасувати", callback_data=f"shift_manage:{shift_id}")]]
    )

    if field == "date":
        await state.set_state(EditShiftFSM.waiting_for_date)
        await callback.message.edit_text("Введіть нову дату у форматі <b>ДД.ММ.РРРР</b> (наприклад, <code>09.10.2026</code>):", parse_mode=ParseMode.HTML, reply_markup=kb)
    elif field == "pallets":
        await state.set_state(EditShiftFSM.waiting_for_pallets)
        await callback.message.edit_text("Введіть нову кількість палет (число, наприклад <code>16</code> або <code>16.5</code>):", parse_mode=ParseMode.HTML, reply_markup=kb)
    elif field == "downtime":
        await state.set_state(EditShiftFSM.waiting_for_downtime)
        await callback.message.edit_text("Введіть час простою у хвилинах (наприклад, <code>15</code> або <code>0</code>):", parse_mode=ParseMode.HTML, reply_markup=kb)

    await callback.answer()


# Обробники введення тексту
@router.message(EditShiftFSM.waiting_for_date)
async def process_new_date(message: types.Message, state: FSMContext):
    try:
        new_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неправильний формат! Введіть дату як <b>ДД.ММ.РРРР</b> (наприклад, <code>09.10.2026</code>):", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    shift_id = data["shift_id"]
    await update_shift_date(shift_id, new_date)
    await state.clear()
    await message.answer(f"✅ Дату успішно змінено на {new_date.strftime('%d.%m.%Y')}!")


@router.message(EditShiftFSM.waiting_for_pallets)
async def process_new_pallets(message: types.Message, state: FSMContext):
    try:
        pallets = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer("Будь ласка, введіть коректне число (наприклад, <code>14</code>):", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    shift_id = data["shift_id"]
    await update_shift_pallets(shift_id, pallets)
    await state.clear()
    await message.answer(f"✅ Кількість палет оновлено: <b>{pallets:g} шт.</b>", parse_mode=ParseMode.HTML)


@router.message(EditShiftFSM.waiting_for_downtime)
async def process_new_downtime(message: types.Message, state: FSMContext):
    try:
        downtime = int(message.text.strip())
    except ValueError:
        await message.answer("Введіть ціле число хвилин (наприклад, <code>20</code>):", parse_mode=ParseMode.HTML)
        return

    data = await state.get_data()
    shift_id = data["shift_id"]
    await update_shift_downtime(shift_id, downtime)
    await state.clear()
    await message.answer(f"✅ Простій оновлено: <b>{downtime} хв</b>", parse_mode=ParseMode.HTML)