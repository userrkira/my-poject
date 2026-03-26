import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from notify_admin import on_startup_notify
from database.models import async_main
from config_data.config_data import Config, load_config

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import start_handler, sheduler_handler
from handlers.admin_handlers import sites_handler, check_site_handler
from handlers.sheduler_handler import check_sites_func


# Инициализируем logger
logger = logging.getLogger(__name__)

# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,

        # filename="py_log.log",
        # filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    sheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    sheduler.add_job(check_sites_func, 'cron', hour='12', minute='0', args=(bot,))
    sheduler.add_job(check_sites_func, 'cron', hour='0', minute='0', args=(bot,))
    sheduler.start()

    #Регистрация роутеров
    # Старт
    dp.include_router(start_handler.router)

    # Админ
    dp.include_router(sites_handler.router)
    dp.include_router(check_site_handler.router)

    # Sheduler
    dp.include_router(sheduler_handler.router)

    await on_startup_notify(bot=bot)
    await async_main()


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())