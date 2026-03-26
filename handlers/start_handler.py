from aiogram import Bot, types, Router, F
from aiogram.filters import Command
    
import logging
from config_data.config_data import Config, load_config
from keyboard import admin_keyboard
from database.requests import admin_requests

config: Config = load_config()
router = Router()

admin_ids = str(config.tg_bot.admin_ids).split(',')


@router.message(Command('start'))
async def start(message: types.Message):
    """Старт"""
    logging.info('start')
    user_id = str(message.from_user.id)
    if user_id in admin_ids:
        markup = await admin_keyboard.main_buttons()
        await message.answer('Выберите действие 👇', reply_markup=markup)
    else:
        await message.answer('Доступ к боту имеют только авторизованные пользователи ❌')