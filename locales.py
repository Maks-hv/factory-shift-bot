from typing import Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    "btn_add_shift": {"uk": "➕ Записати зміну", "pl": "➕ Zapisz zmianę", "en": "➕ Log Shift"},
    "btn_stats": {"uk": "📊 Статистика", "pl": "📊 Statystyki", "en": "📊 Statistics"},
    "btn_charts": {"uk": "📈 Графіки", "pl": "📈 Wykresy", "en": "📈 Charts"},
    "btn_month_report": {"uk": "📅 Звіт за місяць", "pl": "📅 Raport miesięczny", "en": "📅 Monthly Report"},
    "btn_export_all": {"uk": "📥 Експорт усіх змін", "pl": "📥 Eksport wszystkich", "en": "📥 Export All"},
    "welcome": {
        "uk": (
            "👋 <b>Ласкаво просимо до системи обліку роботи роботів!</b>\n\n"
            "👤 Оператор: <b>{name}</b>\n"
            "🌐 Мова: <b>{lang_name}</b>\n\n"
            "• Змінити ім'я: <code>/set_name Ім'я Прізвище</code>\n"
            "• Пакетний імпорт: <code>/import</code>\n"
            "• Змінити мову: <code>/lang</code>\n"
            "• Записати зміну — кнопка внизу 👇"
        ),
        "pl": (
            "👋 <b>Witamy w systemie rejestracji zmian robotów!</b>\n\n"
            "👤 Operator: <b>{name}</b>\n"
            "🌐 Język: <b>{lang_name}</b>\n\n"
            "• Zmień nazwisko: <code>/set_name Imię Nazwisko</code>\n"
            "• Szybki import: <code>/import</code>\n"
            "• Zmień język: <code>/lang</code>\n"
            "• Zapisz zmianę — przycisk na dole 👇"
        ),
        "en": (
            "👋 <b>Welcome to the Robot Shift Logging System!</b>\n\n"
            "👤 Operator: <b>{name}</b>\n"
            "🌐 Language: <b>{lang_name}</b>\n\n"
            "• Change name: <code>/set_name Name Surname</code>\n"
            "• Bulk import: <code>/import</code>\n"
            "• Change language: <code>/lang</code>\n"
            "• Log shift — button below 👇"
        ),
    },
    "choose_date_prompt": {
        "uk": "👤 Оператор: <b>{name}</b>\n\nОберіть дату зміни:",
        "pl": "👤 Operator: <b>{name}</b>\n\nWybierz datę zmiany:",
        "en": "👤 Operator: <b>{name}</b>\n\nSelect shift date:",
    },
    "prompt_custom_date": {
        "uk": "Введіть дату у форматі <code>ДД.ММ.РРРР</code> (наприклад, <code>15.09.2026</code>):",
        "pl": "Wpisz datę w formacie <code>DD.MM.RRRR</code> (np. <code>15.09.2026</code>):",
        "en": "Enter date in format <code>DD.MM.YYYY</code> (e.g. <code>15.09.2026</code>):",
    },
    "invalid_date": {
        "uk": "⚠️ Некоректний формат дати. Спробуйте ще раз (наприклад, <code>15.09.2026</code>):",
        "pl": "⚠️ Niepoprawny format daty. Spróbuj ponownie (np. <code>15.09.2026</code>):",
        "en": "⚠️ Invalid date format. Try again (e.g. <code>15.09.2026</code>):",
    },
    "choose_shift_hours": {
        "uk": "📅 Дата: <b>{date}</b>\n👤 Оператор: <b>{name}</b>\n\nОберіть години зміни:",
        "pl": "📅 Data: <b>{date}</b>\n👤 Operator: <b>{name}</b>\n\nWybierz godziny zmiany:",
        "en": "📅 Date: <b>{date}</b>\n👤 Operator: <b>{name}</b>\n\nSelect shift hours:",
    },
    "prompt_custom_hours": {
        "uk": "Напишіть години зміни вручну (наприклад, <code>07:00-19:00</code>):",
        "pl": "Wpisz godziny zmiany ręcznie (np. <code>07:00-19:00</code>):",
        "en": "Enter custom shift hours (e.g. <code>07:00-19:00</code>):",
    },
    "prompt_robot_select": {
        "uk": "<b>Робот #{num}</b>\nОберіть робота / пост:{added}",
        "pl": "<b>Robot #{num}</b>\nWybierz robota / gniazdo:{added}",
        "en": "<b>Robot #{num}</b>\nSelect robot / station:{added}",
    },
    "already_added": {
        "uk": "\n<i>Вже записані: {robots}</i>",
        "pl": "\n<i>Już zapisane: {robots}</i>",
        "en": "\n<i>Already logged: {robots}</i>",
    },
    "prompt_custom_robot": {
        "uk": "Введіть позначення робота вручну (наприклад, K1, K6):",
        "pl": "Wpisz oznaczenie robota ręcznie (np. K1, K6):",
        "en": "Enter robot name manually (e.g. K1, K6):",
    },
    "prompt_pallets": {
        "uk": "Робот: <b>{robot}</b>\nВведіть кількість палет (ціле або десяткове, наприклад <code>14.5</code>):",
        "pl": "Robot: <b>{robot}</b>\nWpisz liczbę palet (np. <code>14.5</code>):",
        "en": "Robot: <b>{robot}</b>\nEnter pallet count (e.g. <code>14.5</code>):",
    },
    "invalid_pallets": {
        "uk": "⚠️ Введіть коректне число палет (наприклад, <code>14</code> або <code>14.5</code>):",
        "pl": "⚠️ Wpisz poprawną liczbę palet (np. <code>14</code> lub <code>14.5</code>):",
        "en": "⚠️ Please enter a valid number (e.g. <code>14</code> or <code>14.5</code>):",
    },
    "prompt_cartons": {
        "uk": "Скільки <b>незібраних коробок</b> залишилося на столі/піддоні? (введіть число або натисніть 0):",
        "pl": "Ile <b>kartonów zostało</b> na stole/palecie? (wpisz liczbę lub kliknij 0):",
        "en": "How many <b>cartons are left</b>? (enter number or tap 0):",
    },
    "invalid_cartons": {
        "uk": "⚠️ Введіть ціле число коробок (≥ 0):",
        "pl": "⚠️ Wpisz liczbę całkowitą (≥ 0):",
        "en": "⚠️ Enter an integer (≥ 0):",
    },
    "prompt_tonnage": {
        "uk": "Скільки це в <b>тоннах</b>? (наприклад: <code>18.5</code>):",
        "pl": "Ile to w <b>tonach</b>? (np. <code>18.5</code>):",
        "en": "How much in <b>tons</b>? (e.g. <code>18.5</code>):",
    },
    "invalid_tonnage": {
        "uk": "⚠️ Введіть коректний тоннаж (число ≥ 0):",
        "pl": "⚠️ Wpisz poprawny tonaż (liczba ≥ 0):",
        "en": "⚠️ Enter valid tonnage (≥ 0):",
    },
    "prompt_downtime_ask": {
        "uk": "Чи були простої (зупинки лінії) на цьому роботі?",
        "pl": "Czy były przestoje (zatrzymanie linii) na tym robocie?",
        "en": "Were there any downtime stops on this robot?",
    },
    "prompt_downtime_minutes": {
        "uk": "Введіть час простою у <b>хвилинах</b> (наприклад, 25):",
        "pl": "Wpisz czas przestoju w <b>minutach</b> (np. 25):",
        "en": "Enter downtime in <b>minutes</b> (e.g. 25):",
    },
    "invalid_minutes": {
        "uk": "⚠️ Введіть число хвилин (більше 0):",
        "pl": "⚠️ Wpisz liczbę minut (> 0):",
        "en": "⚠️ Enter minutes (> 0):",
    },
    "prompt_downtime_reason": {
        "uk": "Оберіть причину простою лінії:",
        "pl": "Wybierz przyczynę przestoju linii:",
        "en": "Select downtime reason:",
    },
    "prompt_custom_reason": {
        "uk": "Опишіть причину простою текстом:",
        "pl": "Opisz przyczynę przestoju tekstem:",
        "en": "Type downtime reason:",
    },
    "prompt_minor_ask": {
        "uk": "Чи була аварія/збій, яка <b>НЕ зупинила</b> лінію (скинули одразу)?",
        "pl": "Czy była awaria/błąd, która <b>NIE zatrzymała</b> linii (skasowano od razu)?",
        "en": "Was there any micro-incident that <b>DID NOT stop</b> the line?",
    },
    "prompt_minor_reason": {
        "uk": "Коротко напишіть причину збою без зупинки:",
        "pl": "Krótko opisz awarię bez przestoju:",
        "en": "Briefly describe the micro-incident:",
    },
    "robot_added_card": {
        "uk": "✅ Дані по <b>{robot}</b> додано!\n• Палети: <b>{pal}</b> (залишок: {krt} кор.)\n• Тоннаж: <b>{ton}</b>\nВсього роботів у зміні: <b>{count}</b>\n\nДодати ще робота чи завершити?",
        "pl": "✅ Dane dla <b>{robot}</b> dodane!\n• Palety: <b>{pal}</b> (zostało: {krt} krt)\n• Tonaż: <b>{ton}</b>\nŁącznie robotów w zmianie: <b>{count}</b>\n\nDodać kolejnego czy zakończyć?",
        "en": "✅ Data for <b>{robot}</b> added!\n• Pallets: <b>{pal}</b> (cartons left: {krt})\n• Tonnage: <b>{ton}</b>\nTotal robots in shift: <b>{count}</b>\n\nAdd another or finish?",
    },
    "btn_history_30": {
        "uk": "📋 Останні 30 днів",
        "pl": "📋 Ostatnie 30 dni",
        "en": "📋 Last 30 days",
    },
    

    "shift_canceled": {"uk": "❌ Запис зміни скасовано.", "pl": "❌ Zapis zmiany anulowany.", "en": "❌ Shift logging canceled."},
    "shift_saved_success": {
        "uk": "✅ <b>Зміну збережено!</b>\n\nЗвіт для бригадира (натисніть, щоб скопіювати):\n\n<code>{report}</code>",
        "pl": "✅ <b>Zmiana zapisana!</b>\n\nRaport dla brygadzisty (kliknij, aby skopiować):\n\n<code>{report}</code>",
        "en": "✅ <b>Shift saved!</b>\n\nSupervisor report (tap to copy):\n\n<code>{report}</code>",
    },
    "stats_empty": {"uk": "У вас ще немає збережених змін.", "pl": "Brak zapisanych zmian.", "en": "No recorded shifts found."},
    "stats_card": {
        "uk": (
            "<b>📊 Зведення за останні {shifts_cnt} змін:</b>\n"
            "• Оператор: <b>{name}</b>\n\n"
            "• Відпрацьовано змін: <b>{shifts_cnt}</b>\n"
            "• Задіяно роботів: <b>{robots_cnt}</b>\n"
            "• Вироблено палет: <b>{pallets:.1f} шт.</b>\n"
            "• Загальний тоннаж: <b>{tonnage:.2f} т</b>\n"
            "• Середня виробітка: <b>{avg_pal:.1f} пал./зміна</b> (~{avg_ton:.2f} т)\n"
            "• Сумарні простої: <b>{downtime} хв.</b>"
        ),
        "pl": (
            "<b>📊 Podsumowanie ostatnich {shifts_cnt} zmian:</b>\n"
            "• Operator: <b>{name}</b>\n\n"
            "• Przepracowane zmiany: <b>{shifts_cnt}</b>\n"
            "• Roboty: <b>{robots_cnt}</b>\n"
            "• Palety: <b>{pallets:.1f} szt.</b>\n"
            "• Tonaż: <b>{tonnage:.2f} t</b>\n"
            "• Średnia wydajność: <b>{avg_pal:.1f} pal./zmiana</b> (~{avg_ton:.2f} t)\n"
            "• Przestoje: <b>{downtime} min.</b>"
        ),
        "en": (
            "<b>📊 Summary of the last {shifts_cnt} shifts:</b>\n"
            "• Operator: <b>{name}</b>\n\n"
            "• Shifts: <b>{shifts_cnt}</b>\n"
            "• Robot stations: <b>{robots_cnt}</b>\n"
            "• Pallets: <b>{pallets:.1f} pcs</b>\n"
            "• Tonnage: <b>{tonnage:.2f} t</b>\n"
            "• Avg output: <b>{avg_pal:.1f} pal./shift</b> (~{avg_ton:.2f} t)\n"
            "• Total downtime: <b>{downtime} min.</b>"
        ),
    },
}


def t(key: str, lang: str = "uk", **kwargs) -> str:
    lang_dict = MESSAGES.get(key, {})
    raw_text = lang_dict.get(lang, lang_dict.get("uk", key))
    if kwargs:
        return raw_text.format(**kwargs)
    return raw_text