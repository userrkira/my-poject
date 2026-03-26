from aiogram import Bot, types, Router, F

import logging
import requests

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard
from database.requests import admin_requests

config: Config = load_config()
router = Router()


@router.message(F.text == 'Проверить работу ⚙️')
async def check_site_work(message: types.Message):
    """Выбор сайта для проверки работы"""
    logging.info('check_site_work')
    sites_data = await admin_requests.get_all_sites()
    if sites_data:
        markup = await admin_keyboard.pagination_sites('select-site-check', 'pagination-site-check', sites_data, 0, False)
        await message.answer('Выберите сайт для проверки работы 👇', reply_markup=markup)
    else:
        await message.answer('Вы не добавили еще не одного сайта ❌')


@router.callback_query(F.data.startswith('pagination-site-check_'))
async def pagination_sites_to_check(callback: types.CallbackQuery):
    """Пагинация сайтов для проверки"""
    logging.info('pagination_sites_to_check')
    index = int(str(callback.data).split('_')[1])

    sites_data = await admin_requests.get_all_sites()
    markup = await admin_keyboard.pagination_sites('select-site-check', 'pagination-site-check', sites_data, index, False)

    if markup:
        await callback.message.edit_text('Выберите сайт для проверки работы 👇', reply_markup=markup)
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-site-check_'))
async def select_site_to_check(callback: types.CallbackQuery):
    """Выбор сайта и проверка работы"""
    logging.info('select_site_to_check')
    index = int(str(callback.data).split('_')[1])

    site_url = await admin_requests.get_site_by_id(index)
    markup = await admin_keyboard.back_button('pagination-site-check_0')
    try:
        check_site = requests.get(site_url, timeout=5)
        if check_site.status_code == 200:
            await callback.message.edit_text(f'Ответ от сайта получен, сайт: {site_url} работает ✅', reply_markup=markup)
        else:
            await callback.message.edit_text(f'Не удалось получить ответ от сайта: {site_url} ❌ Код ошибки: {check_site.status_code}', reply_markup=markup)

    except Exception as e:
        logging.info(f'Не удалось проверить работу сайта: {site_url}')
        await callback.message.edit_text(f'Не удалось получить ответ от сайта: {site_url} ❌ Домен не существует', reply_markup=markup)


@router.callback_query(F.data == 'check-all-sites')
async def check_all_sites(callback: types.CallbackQuery, bot: Bot):
    """Проверка всех сайтов сразу"""
    logging.info('check_all_sites')
    send_message = await callback.message.edit_text('Выполняю проверку сайтов ⏳ ...')

    sites_data = await admin_requests.get_all_sites()
    markup = await admin_keyboard.back_button('pagination-site-check_0')

    text_good = 'В порядке ✅ 👇\n'
    text_bad = '\nНе работают ❌ 👇\n'

    for site in sites_data:
        site = site.__dict__
        try:
            check_site = requests.get(site['url'], timeout=5)
            if check_site.status_code == 200:
                text_good += site['url'] + '\n'
            else:
                text_bad += site['url'] + '\n' + f'Код ошибки: {check_site.status_code}'
        except Exception as e:
            text_bad += site['url'] + ' Домен не существует'

    text_end = 'Состояние сайтов:\n\n' + text_good + text_bad
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=send_message.message_id,
                                text=text_end,
                                reply_markup=markup)












