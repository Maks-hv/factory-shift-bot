from datetime import date
import io
from typing import Sequence
from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from analytics.charts import build_downtime_pie_chart, build_pallets_bar_chart
from database.models import Shift
from database.requests import (
    get_all_user_shifts,
    get_user_recent_shifts,
    get_user_settings,
    get_user_shifts_for_month,
    get_user_shifts_for_period,
)
from keyboards.shifts_kb import get_month_picker_kb
from locales import t

reports_router = Router()


def build_printable_monthly_excel(
    shifts: Sequence[Shift],
    operator_name: str,
    year: int,
    month: int,
) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{year}_{month:02d}"

    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    ws.page_margins.left = 0.35
    ws.page_margins.right = 0.35
    ws.page_margins.top = 0.5
    ws.page_margins.bottom = 0.5

    DARK_BLUE = "1B365D"
    ICE_BLUE = "E8EEF5"
    ZEBRA_LIGHT = "F9FBFC"
    WHITE = "FFFFFF"
    BORDER_COLOR = "B0BEC5"

    title_font = Font(name="Segoe UI", size=15, bold=True, color=DARK_BLUE)
    sub_font = Font(name="Segoe UI", size=10, italic=True, color="546E7A")
    meta_font = Font(name="Segoe UI", size=10, bold=True, color="263238")
    meta_val_font = Font(name="Segoe UI", size=10, color="37474F")
    header_font = Font(name="Segoe UI", size=10, bold=True, color=WHITE)
    data_font = Font(name="Segoe UI", size=9, color="212121")
    total_font = Font(name="Segoe UI", size=10, bold=True, color=DARK_BLUE)
    metric_font = Font(name="Segoe UI", size=10, bold=True, color="004D40")

    thin_border_side = Side(border_style="thin", color=BORDER_COLOR)
    double_bottom_side = Side(border_style="double", color=DARK_BLUE)
    table_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    total_border = Border(top=thin_border_side, bottom=double_bottom_side, left=thin_border_side, right=thin_border_side)

    header_fill = PatternFill(start_color=DARK_BLUE, end_color=DARK_BLUE, fill_type="solid")
    zebra_fill = PatternFill(start_color=ZEBRA_LIGHT, end_color=ZEBRA_LIGHT, fill_type="solid")
    total_fill = PatternFill(start_color=ICE_BLUE, end_color=ICE_BLUE, fill_type="solid")

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center")

    months_pl = [
        "", "STYCZEŃ", "LUTY", "MARZEC", "KWIECIEŃ", "MAJ", "CZERWIEC",
        "LIPIEC", "SIERPIEŃ", "WRZESIEŃ", "PAŹDZIERNIK", "LISTOPAD", "GRUDZIEŃ",
    ]

    ws.merge_cells("A1:H1")
    ws["A1"] = "MIESIĘCZNY RAPORT PRACY ROBOTÓW PALETYZACJI"
    ws["A1"].font = title_font

    ws.merge_cells("A2:H2")
    ws["A2"] = f"Okres rozliczeniowy: {months_pl[month]} {year}"
    ws["A2"].font = sub_font

    ws["A4"] = "Operator:"
    ws["A4"].font = meta_font
    ws["B4"] = operator_name
    ws["B4"].font = meta_val_font

    ws["F4"] = "Data wygenerowania:"
    ws["F4"].font = meta_font
    ws["F4"].alignment = align_right
    ws["G4"] = date.today().strftime("%Y-%m-%d")
    ws["G4"].font = meta_val_font

    headers = [
        "Data",
        "Godziny zmiany",
        "Robot",
        "Palety\n[szt.]",
        "Pozostało\n[krt]",
        "Przestój\n[min]",
        "Przyczyna przestoju",
        "Zdarzenia / mikroawarie (bez przestoju)",
    ]
    start_row = 6
    ws.row_dimensions[start_row].height = 28

    for col_idx, header_text in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=header_text)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = table_border

    current_row = start_row + 1
    row_count = 0

    for s in shifts:
        for r in s.robots:
            row_count += 1
            ws.row_dimensions[current_row].height = 20

            c_date = ws.cell(row=current_row, column=1, value=s.date.strftime("%Y-%m-%d"))
            c_hours = ws.cell(row=current_row, column=2, value=s.shift_hours)
            c_robot = ws.cell(row=current_row, column=3, value=r.machine)
            c_pal = ws.cell(row=current_row, column=4, value=r.pallets_count)
            c_krt = ws.cell(row=current_row, column=5, value=r.cartons_left)
            c_dt = ws.cell(row=current_row, column=6, value=r.downtime_minutes)
            c_reason = ws.cell(row=current_row, column=7, value=r.downtime_reason or "-")
            c_minor = ws.cell(row=current_row, column=8, value=r.minor_incident_note or "-")

            c_date.alignment = align_center
            c_hours.alignment = align_center
            c_robot.alignment = align_center
            c_pal.alignment = align_right
            c_krt.alignment = align_right
            c_dt.alignment = align_right
            c_reason.alignment = align_left
            c_minor.alignment = align_left

            c_pal.number_format = "#,##0.0"

            for c in (c_date, c_hours, c_robot, c_pal, c_krt, c_dt, c_reason, c_minor):
                c.font = data_font
                c.border = table_border
                if row_count % 2 == 0:
                    c.fill = zebra_fill
            current_row += 1

    if row_count > 0:
        total_shifts_count = len(shifts)
        planned_minutes = total_shifts_count * 480

        ws.row_dimensions[current_row].height = 24
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        lbl = ws.cell(row=current_row, column=1, value="RAZEM / PODSUMOWANIE:")
        lbl.font = total_font
        lbl.alignment = Alignment(horizontal="right", vertical="center")

        sum_pallets = ws.cell(row=current_row, column=4, value=f"=SUM(D{start_row + 1}:D{current_row - 1})")
        sum_pallets.font = total_font
        sum_pallets.alignment = align_right
        sum_pallets.number_format = "#,##0.0"

        sum_cartons = ws.cell(row=current_row, column=5, value=f"=SUM(E{start_row + 1}:E{current_row - 1})")
        sum_cartons.font = total_font
        sum_cartons.alignment = align_right

        sum_dt = ws.cell(row=current_row, column=6, value=f"=SUM(F{start_row + 1}:F{current_row - 1})")
        sum_dt.font = total_font
        sum_dt.alignment = align_right

        for col_idx in range(1, 9):
            ws.cell(row=current_row, column=col_idx).border = total_border
            ws.cell(row=current_row, column=col_idx).fill = total_fill

        kpi_row_1 = current_row + 2
        ws.cell(row=kpi_row_1, column=2, value="Średnia wydajność na zmianę:").font = metric_font
        avg_cell = ws.cell(row=kpi_row_1, column=4, value=f"=D{current_row}/{total_shifts_count}")
        avg_cell.font = metric_font
        avg_cell.number_format = "#,##0.1"

        kpi_row_2 = current_row + 3
        ws.cell(row=kpi_row_2, column=2, value="Dostępność linii (OEE preview):").font = metric_font
        oee_cell = ws.cell(row=kpi_row_2, column=4, value=f"=({planned_minutes}-F{current_row})/{planned_minutes}")
        oee_cell.font = metric_font
        oee_cell.number_format = "0.0%"

        sign_row = current_row + 5
        ws.cell(row=sign_row, column=2, value="Podpis Operatora: ..............................").font = meta_val_font
        ws.cell(row=sign_row, column=7, value="Podpis Mistrza / Kierownika: ..............................").font = meta_val_font

    col_widths = {"A": 12, "B": 15, "C": 9, "D": 12, "E": 12, "F": 12, "G": 30, "H": 36}
    for col_letter, width in col_widths.items():
        ws.column_dimensions[col_letter].width = width

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


@reports_router.message(F.text.in_({"📈 Графіки", "📈 Wykresy", "📈 Charts"}))
async def handle_send_analytics_charts(message: Message) -> None:
    shifts = await get_user_shifts_for_period(message.from_user.id, days=14)
    if not shifts:
        await message.answer("Недостатньо даних для генерації графіків (потрібно хоча б 1 збережена зміна).")
        return

    await message.answer("📊 Формую аналітичні графіки...")

    bar_buf = build_pallets_bar_chart(shifts, days=14)
    if bar_buf:
        photo_bar = BufferedInputFile(bar_buf.getvalue(), filename="production_chart.png")
        await message.answer_photo(photo=photo_bar, caption="📈 <b>Виробіток палет по роботах (останні 14 днів)</b>", parse_mode="HTML")

    pie_buf = build_downtime_pie_chart(shifts)
    if pie_buf:
        photo_pie = BufferedInputFile(pie_buf.getvalue(), filename="downtime_chart.png")
        await message.answer_photo(photo=photo_pie, caption="⏱ <b>Розподіл причин простоїв лінії</b>", parse_mode="HTML")


@reports_router.message(F.text.in_({"📅 Звіт за місяць", "📅 Raport miesięczny", "📅 Monthly Report"}))
async def ask_month_selection(message: Message) -> None:
    _, lang = await get_user_settings(message.from_user.id)
    await message.answer("Оберіть період для формування чистового звіту Excel:", reply_markup=get_month_picker_kb(lang))


@reports_router.callback_query(F.data.startswith("export_month:"))
async def process_month_export(callback: CallbackQuery) -> None:
    _, year_s, month_s = callback.data.split(":")
    year, month = int(year_s), int(month_s)
    operator_name, _ = await get_user_settings(callback.from_user.id)

    shifts = await get_user_shifts_for_month(callback.from_user.id, year=year, month=month)
    if not shifts:
        await callback.message.edit_text(f"⚠️ За {month:02d}.{year} змін не знайдено.")
        await callback.answer()
        return

    excel_file = build_printable_monthly_excel(shifts=shifts, operator_name=operator_name, year=year, month=month)
    filename = f"Raport_Robotow_{year}_{month:02d}.xlsx"
    doc = BufferedInputFile(excel_file.getvalue(), filename=filename)

    await callback.message.delete()
    await callback.message.answer_document(
        document=doc,
        caption=(
            f"📄 <b>Чистовий місячний табель за {month:02d}.{year}</b>\n\n"
            f"• Оператор: <b>{operator_name}</b>\n"
            f"• Змін: <b>{len(shifts)}</b>\n"
            "• Формат: <b>A4 Landscape</b> з інженерними OEE-метриками."
        ),
        parse_mode="HTML",
    )
    await callback.answer()


@reports_router.message(F.text.in_({"📥 Експорт усіх змін", "📥 Eksport wszystkich", "📥 Export All"}))
async def export_all_to_excel(message: Message) -> None:
    operator_name, lang = await get_user_settings(message.from_user.id)
    shifts = await get_all_user_shifts(user_id=message.from_user.id)
    if not shifts:
        await message.answer(t("stats_empty", lang))
        return

    today = date.today()
    excel_file = build_printable_monthly_excel(shifts=shifts, operator_name=operator_name, year=today.year, month=today.month)
    document = BufferedInputFile(excel_file.getvalue(), filename="Pelny_Rejestr_Zmian.xlsx")
    await message.answer_document(document=document, caption="📁 Повний архів ваших змін у форматі A4 Print-Ready.")


@reports_router.message(F.text.in_({"📊 Статистика", "📊 Statystyki", "📊 Statistics"}))
async def show_statistics(message: Message) -> None:
    operator_name, lang = await get_user_settings(message.from_user.id)
    shifts = await get_user_recent_shifts(user_id=message.from_user.id, limit=7)

    if not shifts:
        await message.answer(t("stats_empty", lang))
        return

    total_shifts = len(shifts)
    all_entries = [r for s in shifts for r in s.robots]

    total_pallets = sum(r.pallets_count for r in all_entries)
    total_tonnage = sum(r.tonnage for r in all_entries)
    total_downtime = sum(r.downtime_minutes for r in all_entries)
    avg_pallets_per_shift = round(total_pallets / total_shifts, 1)
    avg_tonnage_per_shift = round(total_tonnage / total_shifts, 2)

    await message.answer(
        t(
            "stats_card",
            lang,
            shifts_cnt=total_shifts,
            name=operator_name,
            robots_cnt=len(all_entries),
            pallets=total_pallets,
            tonnage=total_tonnage,
            avg_pal=avg_pallets_per_shift,
            avg_ton=avg_tonnage_per_shift,
            downtime=total_downtime,
        ),
        parse_mode="HTML",
    )