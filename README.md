# 🏭 Industrial Palletizing Shift Automation Bot

An asynchronous production-grade Telegram bot engineered to automate shift logging, operational incident reporting, and performance tracking for robotic palletizing cells on an industrial manufacturing line. 

Eliminates manual paper logs, delivers real-time standardized shift reports in Polish for shift supervisors, and automatically compiles print-ready monthly A4 Excel timesheets with automated **Overall Equipment Effectiveness (OEE)** availability metrics.

---

## 🛠 Tech Stack & Architecture

* **Runtime:** Python 3.11+
* **Framework:** `aiogram 3.x` (FSM, Routers, Inline/Reply dynamic keyboards, memory buffers)
* **Database & ORM:** `SQLAlchemy 2.0` (fully async via `aiosqlite`), SQLite persistence, atomic transactions
* **Reporting Engine:** `openpyxl` (in-memory `.xlsx` generation using `io.BytesIO` configured for A4 landscape print)
* **Data Visualization:** `matplotlib` (`Agg` headless engine, in-memory dark dashboard rendering)
* **Configuration:** `pydantic-settings` + `.env` with strict type validation
* **DevOps & Deployment:** Docker, Docker Compose, Linux VPS (Ubuntu)

---

## 🚀 Key Features

### 1. Shift Recording Engine (Finite State Machine)
* **Fractional Pallet Precision:** Native support for fractional pallet outputs (e.g., `14.5` or `0.5` pallets) with automated normalization.
* **WIP & Leftovers Tracking:** Explicit tracking of residual loose cartons remaining on accumulation tables.
* **Classified Downtime Logging:** Granular categorization of line stoppages (*vacuum gripper failure, carton jams, pallet shortages, upstream starvation*).
* **Minor Incident Log:** Tracking line resets and micro-stoppages resolved without downtime to safeguard shift operators against shift-handover disputes.

### 2. Standardized Supervisor Reporting
* Generates an instant, clean monospaced text card formatted in **Polish** for direct forwarding into industrial team communication channels.

### 3. Bulk Text Batch Import (`/import`)
* Fast-track regex-based parser allowing operators to ingest historical logs or multi-line shorthand drafts inside a single atomic database transaction.

### 4. Headless Visual Analytics
* **14-Day Production Run:** Stacked bar charts depicting daily pallet counts broken down per robotic cell.
* **Downtime Distribution:** Donut charts illustrating operational losses by category in minutes and percentages.

### 5. Print-Ready Monthly Timesheet (A4 Landscape)
* Fully styled `.xlsx` ledger with custom cell formatting, thin grid borders, zebra rows, and explicit landscape print constraints (`fitToWidth = 1`).
* **Engineering OEE Calculation:** Automated Excel formulas calculating line availability:
  $$\text{Availability} = \frac{\text{Planned Time} - \text{Downtime}}{\text{Planned Time}} \times 100\%$$
* Sign-off blocks for shift operator and production supervisor (`Podpis Mistrza / Kierownika`).

### 6. Multi-Language Operator UI
* Multi-language interface supporting English, Polish, and Ukrainian (`/lang`), while preserving Polish for technical documents and line reports.

---

## 📂 Project Structure

```text
shift_bot/
├── analytics/           # Headless matplotlib chart generators
├── database/            # Async SQLAlchemy models, sessions, and CRUD operations
├── handlers/            # FSM dialogs, command handlers, reports, and bulk imports
├── keyboards/           # Inline and reply UI keyboards
├── locales.py           # Multi-language localization dictionaries
├── config.py            # Pydantic environment configuration
├── main.py              # Entry point and long-polling runner
├── .env.example         # Template for environment secrets
├── .gitignore           # Git ignore policy
└── requirements.txt     # Python project dependencies