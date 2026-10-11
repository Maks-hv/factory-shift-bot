from datetime import date, timedelta
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from locales import t


def get_language_picker_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="set_lang:uk"),
                InlineKeyboardButton(text="🇵🇱 Polski", callback_data="set_lang:pl"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
            ]
        ]
    )


def get_main_menu_kb(lang: str = "uk") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_add_shift", lang))],
            [
                KeyboardButton(text=t("btn_stats", lang)),
                KeyboardButton(text=t("btn_charts", lang)),
                KeyboardButton(text=t("btn_month_report", lang)),
            ],
            [KeyboardButton(text=t("btn_export_all", lang))],
        ],
        resize_keyboard=True,
    )


def get_date_picker_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    today = date.today()
    yesterday = today - timedelta(days=1)

    labels = {
        "uk": (f"Сьогодні ({today.strftime('%d.%m')})", f"Вчора ({yesterday.strftime('%d.%m')})", "📅 Інша дата"),
        "pl": (f"Dzisiaj ({today.strftime('%d.%m')})", f"Wczoraj ({yesterday.strftime('%d.%m')})", "📅 Inna data"),
        "en": (f"Today ({today.strftime('%d.%m')})", f"Yesterday ({yesterday.strftime('%d.%m')})", "📅 Other date"),
    }[lang]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=labels[0], callback_data=f"shift_date:{today.isoformat()}"),
                InlineKeyboardButton(text=labels[1], callback_data=f"shift_date:{yesterday.isoformat()}"),
            ],
            [InlineKeyboardButton(text=labels[2], callback_data="shift_date:custom")],
        ]
    )


def get_shift_time_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    custom_label = {"uk": "✍️ Свої години", "pl": "✍️ Inne godziny", "en": "✍️ Custom hours"}[lang]
    shift1 = {"uk": "1 зміна (07:00 - 15:00)", "pl": "1 zmiana (07:00 - 15:00)", "en": "1st shift (07:00 - 15:00)"}[lang]
    shift2 = {"uk": "2 зміна (15:00 - 23:00)", "pl": "2 zmiana (15:00 - 23:00)", "en": "2nd shift (15:00 - 23:00)"}[lang]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=shift1, callback_data="shift_time:07:00-15:00")],
            [InlineKeyboardButton(text=shift2, callback_data="shift_time:15:00-23:00")],
            [InlineKeyboardButton(text=custom_label, callback_data="shift_time:custom")],
        ]
    )


def get_machine_choice_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    other_label = {"uk": "Інший", "pl": "Inny", "en": "Other"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="К2", callback_data="robot:K2"),
                InlineKeyboardButton(text="К4", callback_data="robot:K4"),
                InlineKeyboardButton(text="К13", callback_data="robot:K13"),
            ],
            [
                InlineKeyboardButton(text="К14", callback_data="robot:K14"),
                InlineKeyboardButton(text="К15", callback_data="robot:K15"),
                InlineKeyboardButton(text=other_label, callback_data="robot:custom"),
            ],
        ]
    )


def get_pallets_input_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    half_pallet_label = {"uk": "➕ Пів палети (0.5)", "pl": "➕ Pół palety (0.5)", "en": "➕ Half pallet (0.5)"}[lang]
    idle_label = {
        "uk": "🚫 Робот не працював (немає продукції)",
        "pl": "🚫 Robot nie pracował (brak produktu)",
        "en": "🚫 Robot idle (no product / no plan)",
    }[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=half_pallet_label, callback_data="pallet_val:0.5")],
            [InlineKeyboardButton(text=idle_label, callback_data="robot_idle:no_product")],
        ]
    )


def get_cartons_prompt_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    zero_label = {"uk": "0 коробок (пропустити)", "pl": "0 kartonów (pomiń)", "en": "0 cartons (skip)"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=zero_label, callback_data="cartons:0")]
        ]
    )


def get_skip_tonnage_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    label = {"uk": "➡️ Пропустити", "pl": "➡️ Pomiń", "en": "➡️ Skip"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data="tonnage:skip")]]
    )


def get_has_downtime_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    no_btn = {"uk": "Ні, лінія не стояла", "pl": "Nie, brak przestojów", "en": "No downtime"}[lang]
    yes_btn = {"uk": "Так, були простої", "pl": "Так, були простої", "en": "Yes, had downtime"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=no_btn, callback_data="downtime:no")],
            [InlineKeyboardButton(text=yes_btn, callback_data="downtime:yes")],
        ]
    )


def get_downtime_reasons_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    labels = {
        "uk": ("Збій захоплення / вакууму", "Зам'яття картону / тари", "Немає палет / прокладок", "Очікування продукту з лінії", "Своя причина"),
        "pl": ("Awaria chwytaka / próżni", "Zacięcie kartonu / opakowania", "Brak palet / przekładek", "Brak produktu z linii", "Własna przyczyna"),
        "en": ("Gripper / vacuum failure", "Cardboard jam", "No pallets / slip sheets", "Waiting for product from line", "Custom reason"),
    }[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=labels[0], callback_data="d_reason:Awaria chwytaka")],
            [InlineKeyboardButton(text=labels[1], callback_data="d_reason:Zacięcie kartonu")],
            [InlineKeyboardButton(text=labels[2], callback_data="d_reason:Brak palet / przekładek")],
            [InlineKeyboardButton(text=labels[3], callback_data="d_reason:Brak produktu z linii")],
            [InlineKeyboardButton(text=labels[4], callback_data="d_reason:custom")],
        ]
    )


def get_minor_incident_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    no_btn = {"uk": "Ні, збоїв не було", "pl": "Nie, brak awarii", "en": "No issues"}[lang]
    yes_btn = {"uk": "Була аварія (без простою)", "pl": "Była awaria (bez przestoju)", "en": "Yes, micro-stop only"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=no_btn, callback_data="minor:no")],
            [InlineKeyboardButton(text=yes_btn, callback_data="minor:yes")],
        ]
    )


def get_next_step_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    add_btn = {"uk": "➕ Додати ще одного робота", "pl": "➕ Dodaj kolejnego robota", "en": "➕ Add another robot"}[lang]
    finish_btn = {"uk": "🏁 Завершити та зберегти", "pl": "🏁 Zakończ i zapisz", "en": "🏁 Finish and save"}[lang]
    cancel_btn = {"uk": "❌ Скасувати все", "pl": "❌ Anuluj wszystko", "en": "❌ Cancel all"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=add_btn, callback_data="next_step:add_another")],
            [InlineKeyboardButton(text=finish_btn, callback_data="next_step:finish")],
            [InlineKeyboardButton(text=cancel_btn, callback_data="next_step:cancel")],
        ]
    )


def get_confirm_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    confirm_btn = {"uk": "✅ Підтвердити і зберегти", "pl": "✅ Potwierdź i zapisz", "en": "✅ Confirm & save"}[lang]
    cancel_btn = {"uk": "❌ Скасувати", "pl": "❌ Anuluj", "en": "❌ Cancel"}[lang]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=confirm_btn, callback_data="final_action:confirm"),
                InlineKeyboardButton(text=cancel_btn, callback_data="final_action:cancel"),
            ]
        ]
    )


def get_month_picker_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    today = date.today()
    curr_y, curr_m = today.year, today.month
    prev_m = 12 if curr_m == 1 else curr_m - 1
    prev_y = curr_y - 1 if curr_m == 1 else curr_y

    months = {
        "uk": ["", "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень", "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"],
        "pl": ["", "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"],
        "en": ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    }[lang]

    curr_label = f"Поточний ({months[curr_m]} {curr_y})" if lang == "uk" else f"Bieżący ({months[curr_m]} {curr_y})"
    prev_label = f"Минулий ({months[prev_m]} {prev_y})" if lang == "uk" else f"Poprzedni ({months[prev_m]} {prev_y})"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=curr_label, callback_data=f"export_month:{curr_y}:{curr_m}")],
            [InlineKeyboardButton(text=prev_label, callback_data=f"export_month:{prev_y}:{prev_m}")],
        ]
    )