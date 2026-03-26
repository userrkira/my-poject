from aiogram import Bot, types, Router, F

import logging
import requests

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard
from database.requests import admin_requests

config: Config = load_config()
router = Router()

admin_ids = str(config.tg_bot.admin_ids).split(',')


async def check_sites_func(bot: Bot):
    """Проверка работы сайтов в 12:00"""
    logging.info('check_sites_sheduler')
    sites_data = await admin_requests.get_all_sites()

    text_good = 'В порядке ✅ 👇\n'
    text_bad = '\nНе работают ❌ 👇\n'

    for site in sites_data:
        site = site.__dict__
        try:
            check_site = requests.get(site['url'], timeout=5)
            if check_site.status_code == 200:
                text_good += site['url'] + '\n'
            else:
                text_bad +=  site['url'] + '\n' + f'Код ошибки: {check_site.status_code}'
        except Exception as e:
            text_bad +=  site['url'] + '\nДомен не существует'

    text_end = 'Состояние сайтов:\n\n' + text_good + text_bad
    for admin_id in admin_ids:
        try:
            await bot.send_message(chat_id=int(admin_id), text=text_end)
        except:
            pass

