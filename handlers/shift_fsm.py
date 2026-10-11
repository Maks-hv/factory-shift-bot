from datetime import date, datetime
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.requests import (
    get_user_settings,
    save_complete_shift,
    set_user_language,
    set_user_operator_name,
)
from keyboards.shifts_kb import (
    get_cartons_prompt_kb,
    get_confirm_kb,
    get_date_picker_kb,
    get_downtime_reasons_kb,
    get_has_downtime_kb,
    get_language_picker_kb,
    get_machine_choice_kb,
    get_main_menu_kb,
    get_minor_incident_kb,
    get_next_step_kb,
    get_pallets_input_kb,
    get_shift_time_kb,
    get_skip_tonnage_kb,
)
from locales import t

shift_router = Router()


class NameChangeFSM(StatesGroup):
    waiting_for_name = State()


class ShiftLogFSM(StatesGroup):
    shift_date = State()
    shift_date_custom = State()
    shift_time = State()
    shift_time_custom = State()
    machine = State()
    machine_custom = State()
    pallets_count = State()
    cartons_left = State()
    tonnage = State()
    has_downtime = State()
    downtime_minutes = State()
    downtime_reason = State()
    minor_incident = State()
    minor_incident_reason = State()
    intermediate_menu = State()
    confirm = State()


@shift_router.message(Command("lang"))
async def cmd_language(message: Message) -> None:
    await message.answer("🌐 <b>Select language / Wybierz język / Оберіть мову:</b>", reply_markup=get_language_picker_kb(), parse_mode="HTML")


@shift_router.callback_query(F.data.startswith("set_lang:"))
async def process_language_choice(callback: CallbackQuery) -> None:
    lang = callback.data.split(":")[1]
    await set_user_language(callback.from_user.id, lang)
    name, _ = await get_user_settings(callback.from_user.id)
    lang_names = {"uk": "Українська", "pl": "Polski", "en": "English"}

    await callback.message.delete()
    await callback.message.answer(
        t("welcome", lang, name=name, lang_name=lang_names.get(lang, lang)),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@shift_router.message(Command("set_name"))
async def cmd_set_name(message: Message, state: FSMContext) -> None:
    _, lang = await get_user_settings(message.from_user.id)
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].strip():
        new_name = args[1].strip()
        await set_user_operator_name(message.from_user.id, new_name)
        await message.answer(f"✅ <b>{new_name}</b>", parse_mode="HTML")
        return

    await state.set_state(NameChangeFSM.waiting_for_name)
    name, _ = await get_user_settings(message.from_user.id)
    await message.answer(f"Поточне ім'я: <b>{name}</b>\nВведіть нове ім'я та прізвище:", parse_mode="HTML")


@shift_router.message(NameChangeFSM.waiting_for_name)
async def process_new_operator_name(message: Message, state: FSMContext) -> None:
    new_name = message.text.strip()
    if len(new_name) < 2 or len(new_name) > 100:
        await message.answer("⚠️ Ім'я має містити від 2 до 100 символів:")
        return

    await set_user_operator_name(message.from_user.id, new_name)
    await state.clear()
    await message.answer(f"✅ Оновлено: <b>{new_name}</b>", parse_mode="HTML")


@shift_router.message(F.text.in_({"➕ Записати зміну", "➕ Zapisz zmianę", "➕ Log Shift"}))
async def start_shift_log(message: Message, state: FSMContext) -> None:
    await state.clear()
    operator_name, lang = await get_user_settings(message.from_user.id)
    await state.update_data(robots=[], operator_name=operator_name, lang=lang)
    await state.set_state(ShiftLogFSM.shift_date)
    await message.answer(t("choose_date_prompt", lang, name=operator_name), reply_markup=get_date_picker_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.shift_date, F.data.startswith("shift_date:"))
async def process_shift_date_choice(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    choice = callback.data.split(":")[1]

    if choice == "custom":
        await state.set_state(ShiftLogFSM.shift_date_custom)
        await callback.message.edit_text(t("prompt_custom_date", lang), parse_mode="HTML")
        await callback.answer()
        return

    selected_date = date.fromisoformat(choice)
    await state.update_data(date=selected_date)
    await state.set_state(ShiftLogFSM.shift_time)
    await callback.message.edit_text(
        t("choose_shift_hours", lang, date=selected_date.strftime("%Y-%m-%d"), name=data["operator_name"]),
        reply_markup=get_shift_time_kb(lang),
        parse_mode="HTML",
    )
    await callback.answer()


@shift_router.message(ShiftLogFSM.shift_date_custom)
async def process_custom_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    raw_text = message.text.strip()
    parsed_date = None
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            parsed_date = datetime.strptime(raw_text, fmt).date()
            break
        except ValueError:
            pass

    if not parsed_date:
        await message.answer(t("invalid_date", lang), parse_mode="HTML")
        return

    await state.update_data(date=parsed_date)
    await state.set_state(ShiftLogFSM.shift_time)
    await message.answer(
        t("choose_shift_hours", lang, date=parsed_date.strftime("%Y-%m-%d"), name=data["operator_name"]),
        reply_markup=get_shift_time_kb(lang),
        parse_mode="HTML",
    )


@shift_router.callback_query(ShiftLogFSM.shift_time, F.data.startswith("shift_time:"))
async def process_shift_time(callback: CallbackQuery, state: FSMContext) -> None:
    choice = callback.data.split(":")[1]
    if choice == "custom":
        await state.set_state(ShiftLogFSM.shift_time_custom)
        await callback.message.edit_text(t("prompt_custom_hours", "uk"), parse_mode="HTML")
        await callback.answer()
        return

    await state.update_data(shift_hours=choice)
    await prompt_next_robot(callback.message, state)
    await callback.answer()


@shift_router.message(ShiftLogFSM.shift_time_custom)
async def process_shift_time_custom(message: Message, state: FSMContext) -> None:
    await state.update_data(shift_hours=message.text.strip())
    await prompt_next_robot(message, state)


async def prompt_next_robot(event_message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    robots_done = [r["machine"] for r in data.get("robots", [])]
    count = len(robots_done) + 1
    added_text = t("already_added", lang, robots=", ".join(robots_done)) if robots_done else ""

    await state.set_state(ShiftLogFSM.machine)
    msg = t("prompt_robot_select", lang, num=count, added=added_text)
    if event_message.from_user.is_bot:
        await event_message.edit_text(msg, reply_markup=get_machine_choice_kb(lang), parse_mode="HTML")
    else:
        await event_message.answer(msg, reply_markup=get_machine_choice_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.machine, F.data.startswith("robot:"))
async def process_robot_choice(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    choice = callback.data.split(":")[1]

    if choice == "custom":
        await state.set_state(ShiftLogFSM.machine_custom)
        await callback.message.edit_text(t("prompt_custom_robot", lang))
        await callback.answer()
        return

    await state.update_data(current_machine=choice)
    await state.set_state(ShiftLogFSM.pallets_count)
    await callback.message.edit_text(t("prompt_pallets", lang, robot=choice), reply_markup=get_pallets_input_kb(lang), parse_mode="HTML")
    await callback.answer()


@shift_router.message(ShiftLogFSM.machine_custom)
async def process_robot_custom(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    custom_name = message.text.strip().upper()
    await state.update_data(current_machine=custom_name)
    await state.set_state(ShiftLogFSM.pallets_count)
    await message.answer(t("prompt_pallets", lang, robot=custom_name), reply_markup=get_pallets_input_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.pallets_count, F.data == "robot_idle:no_product")
async def process_robot_idle(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    robots = data.get("robots", [])
    entry = {
        "machine": data["current_machine"],
        "pallets_count": 0.0,
        "cartons_left": 0,
        "tonnage": 0.0,
        "has_downtime": False,
        "downtime_minutes": 0,
        "downtime_reason": "Brak produktu / brak planu (nie pracował)",
        "has_minor_incident": False,
        "minor_incident_note": None,
    }
    robots.append(entry)
    await state.update_data(robots=robots)
    await state.set_state(ShiftLogFSM.intermediate_menu)
    lang = data.get("lang", "uk")
    text = t("robot_added_card", lang, robot=entry["machine"], pal=0, krt=0, ton="0.0 t", count=len(robots))
    await callback.message.edit_text(text, reply_markup=get_next_step_kb(lang), parse_mode="HTML")
    await callback.answer()


@shift_router.callback_query(ShiftLogFSM.pallets_count, F.data == "pallet_val:0.5")
async def process_half_pallet(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(current_pallets=0.5)
    await state.set_state(ShiftLogFSM.cartons_left)
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await callback.message.edit_text(t("prompt_cartons", lang), reply_markup=get_cartons_prompt_kb(lang), parse_mode="HTML")
    await callback.answer()


@shift_router.message(ShiftLogFSM.pallets_count)
async def process_pallets_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    raw_text = message.text.strip().replace(",", ".")

    try:
        val = float(raw_text)
        if val < 0:
            raise ValueError
    except ValueError:
        await message.answer(t("invalid_pallets", lang), reply_markup=get_pallets_input_kb(lang))
        return

    await state.update_data(current_pallets=round(val, 1))
    await state.set_state(ShiftLogFSM.cartons_left)
    await message.answer(t("prompt_cartons", lang), reply_markup=get_cartons_prompt_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.cartons_left, F.data == "cartons:0")
async def process_cartons_zero(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(current_cartons=0)
    await state.set_state(ShiftLogFSM.tonnage)
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await callback.message.edit_text(t("prompt_tonnage", lang), reply_markup=get_skip_tonnage_kb(lang), parse_mode="HTML")
    await callback.answer()


@shift_router.message(ShiftLogFSM.cartons_left)
async def process_cartons_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    text = message.text.strip()

    if not text.isdigit() or int(text) < 0:
        await message.answer(t("invalid_cartons", lang), reply_markup=get_cartons_prompt_kb(lang))
        return

    await state.update_data(current_cartons=int(text))
    await state.set_state(ShiftLogFSM.tonnage)
    await message.answer(t("prompt_tonnage", lang), reply_markup=get_skip_tonnage_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.tonnage, F.data == "tonnage:skip")
async def process_skip_tonnage(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await state.update_data(current_tonnage=0.0)
    await state.set_state(ShiftLogFSM.has_downtime)
    await callback.message.edit_text(t("prompt_downtime_ask", lang), reply_markup=get_has_downtime_kb(lang))
    await callback.answer()


@shift_router.message(ShiftLogFSM.tonnage)
async def process_tonnage_input(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    raw_val = message.text.strip().replace(",", ".")

    try:
        tonnage_val = float(raw_val)
        if tonnage_val < 0:
            raise ValueError
    except ValueError:
        await message.answer(t("invalid_tonnage", lang), reply_markup=get_skip_tonnage_kb(lang), parse_mode="HTML")
        return

    await state.update_data(current_tonnage=round(tonnage_val, 2))
    await state.set_state(ShiftLogFSM.has_downtime)
    await message.answer(t("prompt_downtime_ask", lang), reply_markup=get_has_downtime_kb(lang))


@shift_router.callback_query(ShiftLogFSM.has_downtime, F.data.startswith("downtime:"))
async def process_downtime_choice(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    choice = callback.data.split(":")[1]

    if choice == "no":
        await state.update_data(current_has_dt=False, current_dt_min=0, current_dt_reason=None)
        await ask_minor_incident(callback.message, state)
    else:
        await state.update_data(current_has_dt=True)
        await state.set_state(ShiftLogFSM.downtime_minutes)
        await callback.message.edit_text(t("prompt_downtime_minutes", lang), parse_mode="HTML")
    await callback.answer()


@shift_router.message(ShiftLogFSM.downtime_minutes)
async def process_downtime_minutes(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    text = message.text.strip()

    if not text.isdigit() or int(text) <= 0:
        await message.answer(t("invalid_minutes", lang))
        return

    await state.update_data(current_dt_min=int(text))
    await state.set_state(ShiftLogFSM.downtime_reason)
    await message.answer(t("prompt_downtime_reason", lang), reply_markup=get_downtime_reasons_kb(lang))


@shift_router.callback_query(ShiftLogFSM.downtime_reason, F.data.startswith("d_reason:"))
async def process_downtime_reason(callback: CallbackQuery, state: FSMContext) -> None:
    choice = callback.data.split(":")[1]
    if choice == "custom":
        await callback.message.edit_text(t("prompt_custom_reason", "uk"))
        await callback.answer()
        return

    await state.update_data(current_dt_reason=choice)
    await callback.answer()
    await ask_minor_incident(callback.message, state)


@shift_router.message(ShiftLogFSM.downtime_reason)
async def process_custom_downtime_reason(message: Message, state: FSMContext) -> None:
    await state.update_data(current_dt_reason=message.text.strip())
    await ask_minor_incident(message, state)


async def ask_minor_incident(event_message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await state.set_state(ShiftLogFSM.minor_incident)
    text = t("prompt_minor_ask", lang)
    if event_message.from_user.is_bot:
        await event_message.edit_text(text, reply_markup=get_minor_incident_kb(lang), parse_mode="HTML")
    else:
        await event_message.answer(text, reply_markup=get_minor_incident_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.minor_incident, F.data.startswith("minor:"))
async def process_minor_incident(callback: CallbackQuery, state: FSMContext) -> None:
    choice = callback.data.split(":")[1]
    if choice == "no":
        await state.update_data(current_has_minor=False, current_minor_note=None)
        await commit_current_robot(callback.message, state)
    else:
        await state.update_data(current_has_minor=True)
        await state.set_state(ShiftLogFSM.minor_incident_reason)
        await callback.message.edit_text(t("prompt_minor_reason", "uk"))
    await callback.answer()


@shift_router.message(ShiftLogFSM.minor_incident_reason)
async def process_minor_reason_text(message: Message, state: FSMContext) -> None:
    await state.update_data(current_minor_note=message.text.strip())
    await commit_current_robot(message, state)


async def commit_current_robot(event_message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    robots = data.get("robots", [])

    entry = {
        "machine": data["current_machine"],
        "pallets_count": float(data["current_pallets"]),
        "cartons_left": int(data.get("current_cartons", 0)),
        "tonnage": float(data["current_tonnage"]),
        "has_downtime": bool(data["current_has_dt"]),
        "downtime_minutes": int(data["current_dt_min"]),
        "downtime_reason": data["current_dt_reason"],
        "has_minor_incident": bool(data["current_has_minor"]),
        "minor_incident_note": data["current_minor_note"],
    }
    robots.append(entry)
    await state.update_data(robots=robots)
    await state.set_state(ShiftLogFSM.intermediate_menu)

    ton_str = f"{entry['tonnage']} т" if entry["tonnage"] > 0 else "-"
    text = t(
        "robot_added_card",
        lang,
        robot=entry["machine"],
        pal=entry["pallets_count"],
        krt=entry["cartons_left"],
        ton=ton_str,
        count=len(robots),
    )

    if event_message.from_user.is_bot:
        await event_message.edit_text(text, reply_markup=get_next_step_kb(lang), parse_mode="HTML")
    else:
        await event_message.answer(text, reply_markup=get_next_step_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.intermediate_menu, F.data.startswith("next_step:"))
async def process_next_step(callback: CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":")[1]
    if action == "add_another":
        await prompt_next_robot(callback.message, state)
    elif action == "finish":
        await render_full_confirmation(callback.message, state)
    elif action == "cancel":
        await state.clear()
        await callback.message.edit_text("❌ Запис зміни скасовано.")
    await callback.answer()


async def render_full_confirmation(event_message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uk")
    await state.set_state(ShiftLogFSM.confirm)

    lines = [
        "<b>📋 Підсумкова картка зміни:</b>",
        f"• Оператор: <b>{data['operator_name']}</b>",
        f"• Дата: <code>{data['date']}</code>",
        f"• Години: <b>{data['shift_hours']}</b>\n",
    ]

    for idx, r in enumerate(data["robots"], 1):
        if r["pallets_count"] == 0 and r["downtime_reason"] == "Brak produktu / brak planu (nie pracował)":
            lines.append(f"{idx}. <b>{r['machine']}</b>: <i>не працював (немає продукції)</i>")
        else:
            krt_str = f" (+{r['cartons_left']} krt)" if r["cartons_left"] > 0 else ""
            dt_str = f" [Przestoje: {r['downtime_minutes']}m]" if r["has_downtime"] else " [0m]"
            lines.append(f"{idx}. <b>{r['machine']}</b>: {r['pallets_count']} pal.{krt_str}{dt_str}")

    lines.append("\nЗберегти в базу?")
    text = "\n".join(lines)
    if event_message.from_user.is_bot:
        await event_message.edit_text(text, reply_markup=get_confirm_kb(lang), parse_mode="HTML")
    else:
        await event_message.answer(text, reply_markup=get_confirm_kb(lang), parse_mode="HTML")


@shift_router.callback_query(ShiftLogFSM.confirm, F.data.startswith("final_action:"))
async def process_final_action(callback: CallbackQuery, state: FSMContext) -> None:
    action = callback.data.split(":")[1]
    if action == "cancel":
        await state.clear()
        await callback.message.edit_text("❌ Скасовано.")
        await callback.answer()
        return

    data = await state.get_data()
    await save_complete_shift(
        user_id=callback.from_user.id,
        shift_date=data["date"],
        shift_hours=data["shift_hours"],
        robots_data=data["robots"],
        operator_name=data["operator_name"],
    )
    await state.clear()

    report_lines = [
        f"Raport zmianowy ({data['date']}, {data['shift_hours']}):",
        f"Operator: {data['operator_name']}",
    ]
    for r in data["robots"]:
        if r["pallets_count"] == 0 and r["downtime_reason"] == "Brak produktu / brak planu (nie pracował)":
            report_lines.append(f"• {r['machine']}: nie pracował (brak produktu / planu)")
        else:
            ton_part = f" ({r['tonnage']} t)" if r["tonnage"] > 0 else ""
            krt_part = f" (+{r['cartons_left']} krt)" if r["cartons_left"] > 0 else ""
            r_parts = [f"• {r['machine']}: {r['pallets_count']} pal.{krt_part}{ton_part}"]
            if r["has_downtime"]:
                r_parts.append(f"przestoje: {r['downtime_minutes']} min ({r['downtime_reason']})")
            else:
                r_parts.append("brak przestojów")
            if r["has_minor_incident"]:
                r_parts.append(f"awarie bez przestoju: {r['minor_incident_note']}")
            report_lines.append(", ".join(r_parts))

    final_report = "\n".join(report_lines)
    await callback.message.edit_text(t("shift_saved_success", "uk", report=final_report), parse_mode="HTML")
    await callback.answer()