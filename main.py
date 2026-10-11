import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message

from config import config
from database.models import init_db
from database.requests import get_user_settings
from handlers.bulk_import import import_router
from handlers.reports import reports_router
from handlers.shift_fsm import shift_router
from keyboards.shifts_kb import get_main_menu_kb
from locales import t
from handlers.history import router as history_router

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    operator_name, lang = await get_user_settings(message.from_user.id)
    lang_names = {"uk": "Українська", "pl": "Polski", "en": "English"}

    await message.answer(
        t("welcome", lang, name=operator_name, lang_name=lang_names.get(lang, lang)),
        reply_markup=get_main_menu_kb(lang),
        parse_mode="HTML",
    )


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    await init_db()

    await bot.set_my_commands([
        BotCommand(command="start", description="Головне меню"),
        BotCommand(command="import", description="Швидкий імпорт історії"),
        BotCommand(command="lang", description="Змінити мову"),
        BotCommand(command="set_name", description="Змінити ім'я оператора"),
    ])

    dp.include_router(shift_router)
    dp.include_router(import_router)
    dp.include_router(reports_router)
    dp.include_router(history_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")