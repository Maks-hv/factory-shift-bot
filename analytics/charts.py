from collections import defaultdict
import io
from typing import Optional, Sequence
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from database.models import Shift

DARK_BG = "#1A1D20"
CARD_BG = "#212529"
TEXT_COLOR = "#F8F9FA"
GRID_COLOR = "#343A40"
PALETTE = ["#0D6EFD", "#20C997", "#FFC107", "#FD7E14", "#D63384", "#6F42C1", "#0DCAF0"]


def build_pallets_bar_chart(shifts: Sequence[Shift], days: int = 14) -> Optional[io.BytesIO]:
    if not shifts:
        return None

    dates_sorted = sorted(list({s.date for s in shifts}))
    machines_set = sorted(list({r.machine for s in shifts for r in s.robots}))

    if not machines_set:
        return None

    date_labels = [d.strftime("%d.%m") for d in dates_sorted]
    data_by_machine = {m: [0.0] * len(dates_sorted) for m in machines_set}
    date_to_idx = {d: idx for idx, d in enumerate(dates_sorted)}

    for s in shifts:
        idx = date_to_idx[s.date]
        for r in s.robots:
            data_by_machine[r.machine][idx] += r.pallets_count

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor=DARK_BG)
    ax.set_facecolor(CARD_BG)

    bottom_vals = [0.0] * len(dates_sorted)
    for i, machine in enumerate(machines_set):
        color = PALETTE[i % len(PALETTE)]
        values = data_by_machine[machine]
        ax.bar(
            date_labels,
            values,
            bottom=bottom_vals,
            label=machine,
            color=color,
            edgecolor=CARD_BG,
            linewidth=1.2,
            width=0.6,
        )
        bottom_vals = [b + v for b, v in zip(bottom_vals, values)]

    ax.set_title(f"Produkcja palet (ostatnie {days} dni)", fontsize=14, color=TEXT_COLOR, pad=15, weight="bold")
    ax.set_ylabel("Palety [szt.]", fontsize=11, color=TEXT_COLOR)
    ax.grid(axis="y", linestyle="--", alpha=0.3, color=GRID_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper left")

    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=160, facecolor=DARK_BG)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def build_downtime_pie_chart(shifts: Sequence[Shift]) -> Optional[io.BytesIO]:
    reason_minutes = defaultdict(int)

    for s in shifts:
        for r in s.robots:
            if r.has_downtime and r.downtime_minutes > 0:
                reason = r.downtime_reason or "Inna przyczyna"
                reason_minutes[reason] += r.downtime_minutes

    if not reason_minutes:
        return None

    labels = list(reason_minutes.keys())
    sizes = list(reason_minutes.values())

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(8, 5.5), facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=PALETTE[:len(sizes)],
        wedgeprops=dict(width=0.7, edgecolor=DARK_BG, linewidth=2),
        textprops=dict(color=TEXT_COLOR, fontsize=10),
    )

    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_weight("bold")

    total_min = sum(sizes)
    ax.set_title(
        f"Przyczyny przestojów linii (Łącznie: {total_min} min)",
        fontsize=13,
        color=TEXT_COLOR,
        pad=15,
        weight="bold",
    )

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=160, facecolor=DARK_BG)
    plt.close(fig)
    buffer.seek(0)
    return buffer