from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext

import logging
import requests

from config_data.config_data import Config, load_config
from keyboard import admin_keyboard
from database.requests import admin_requests

config: Config = load_config()
router = Router()


class FsmSites(StatesGroup):
    get_url = State()


@router.message(F.text == 'Сайты 💻')
async def main_sites(message: types.Message):
    """Управление сайтами"""
    logging.info('main_sites')
    markup = await admin_keyboard.main_sites_buttons()
    await message.answer('Выберите действие 👇', reply_markup=markup)

###################################################################################
########################### Добавление нового сайта ###############################
###################################################################################

@router.callback_query(F.data == 'add-new-site')
async def add_new_site(callback: types.CallbackQuery, state: FSMContext):
    """Добавление нового сайта"""
    logging.info('add_new_site')
    markup = await admin_keyboard.back_button('back-to-site-menu')
    await state.set_state(FsmSites.get_url)
    await callback.message.edit_text('Введите url сайта в таком формате: https://{домен}', reply_markup=markup)


@router.callback_query(F.data == 'back-to-site-menu')
async def back_to_site_menu(callback: types.CallbackQuery, state: FSMContext):
    """Назад к выбору действия"""
    logging.info('back_to_site_menu')
    markup = await admin_keyboard.main_sites_buttons()
    await state.set_state(default_state)
    await callback.message.edit_text('Выберите действие 👇', reply_markup=markup)


@router.message(StateFilter(FsmSites.get_url))
async def get_url(message: types.Message, state: FSMContext):
    """Получение url сайта"""
    logging.info('get_url')
    url = str(message.text)
    try:
        check_site = requests.get(url, timeout=5)

        if check_site.status_code == 200:
            markup = await admin_keyboard.yes_or_no_buttons('confirm-add-site')
            await state.update_data(url=url)
            await state.set_state(default_state)
            await message.answer(f'Вы уверены что хотите добавить сайт: {url} ?', reply_markup=markup)
        else:
            logging.info(f'Код ошибки от сайта: {check_site.status_code}')
            markup = await admin_keyboard.back_button('back-to-site-menu')
            await message.answer(f'Сайт с таким url недоступен ❌ Код ошибки: {check_site.status_code}\n'
                                 'Попробуйте ввести его еще раз, либо вместо https используйте http 👇', reply_markup=markup)

    except Exception as e:
        logging.info(f'Не удалось получить данных о сайте: {url}')
        markup = await admin_keyboard.back_button('back-to-site-menu')
        await message.answer('Сайт с таким url недоступен ❌\n'
                             'Попробуйте ввести его еще раз 👇, либо вместо https используйте http', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-add-site_'))
async def add_site_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Добавить сайт или нет"""
    logging.info('add_site_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        await state.set_state(default_state)
        await admin_requests.add_new_site(state_data['url'])
        await callback.message.edit_text(f'Сайт {state_data["url"]} успешно добавлен ✅')
    else:
        markup = await admin_keyboard.back_button('back-to-site-menu')
        await state.set_state(FsmSites.get_url)
        await callback.message.edit_text('Введите url сайта в таком формате: https://{домен}', reply_markup=markup)


#######################################################################################
########################### Удаление сайта ############################################
#######################################################################################

@router.callback_query(F.data == 'delete-site')
async def delete_sites_menu(callback: types.CallbackQuery):
    """Выбор сайта для удаления"""
    logging.info('delete_sites_menu')
    sites_data = await admin_requests.get_all_sites()
    if sites_data:
        markup = await admin_keyboard.pagination_sites('select-site-delete', 'pagination-site-delete', sites_data, 0, True)
        await callback.message.edit_text('Выберите сайт для удаления 👇', reply_markup=markup)
    else:
        markup = await admin_keyboard.back_button('back-to-site-menu')
        await callback.message.edit_text('Вы еще не добавили ни одного сайта ❌', reply_markup=markup)


@router.callback_query(F.data.startswith('pagination-site-delete_'))
async def pagination_sites_delete(callback: types.CallbackQuery):
    """Пагинация сайтов для удаления"""
    logging.info('pagination_sites_delete')
    page = int(str(callback.data).split('_')[1])

    sites_data = await admin_requests.get_all_sites()
    markup = await admin_keyboard.pagination_sites('select-site-delete', 'pagination-site-delete', sites_data, page, True)
    if markup:
        await callback.message.edit_text('Выберите сайт для удаления 👇', reply_markup=markup)
    else:
        await callback.answer()


@router.callback_query(F.data.startswith('select-site-delete_'))
async def select_site_to_delete(callback: types.CallbackQuery, state: FSMContext):
    """Выбор сайта для удаления"""
    logging.info('select_site_to_delete')
    index = int(str(callback.data).split('_')[1])

    url = await admin_requests.get_site_by_id(index)
    markup = await admin_keyboard.yes_or_no_buttons('confirm-delete-site')

    await state.update_data(delete_url=url)
    await callback.message.edit_text(f'Вы уверены что хотите удалить сайт: {url} ?', reply_markup=markup)


@router.callback_query(F.data.startswith('confirm-delete-site'))
async def delete_site_or_no(callback: types.CallbackQuery, state: FSMContext):
    """Удалить сайт или нет"""
    logging.info('delete_site_or_no')
    flag = str(callback.data).split('_')[1]
    if flag == 'yes':
        state_data = await state.get_data()
        markup = await admin_keyboard.back_button('delete-site')

        await admin_requests.delete_site(state_data['delete_url'])
        await callback.message.edit_text(f'Сайт {state_data["delete_url"]} успешно удален ✅', reply_markup=markup)

    else:
        sites_data = await admin_requests.get_all_sites()
        markup = await admin_keyboard.pagination_sites('select-site-delete', 'pagination-site-delete', sites_data, 0, True)
        await callback.message.edit_text('Выберите сайт для удаления 👇', reply_markup=markup)


































