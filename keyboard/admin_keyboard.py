from aiogram import types


async def main_buttons():
    markup = types.ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    btn_sites = types.KeyboardButton(text='Сайты 💻')
    btn_check = types.KeyboardButton(text='Проверить работу ⚙️')
    markup.keyboard.append([btn_sites])
    markup.keyboard.append([btn_check])
    return markup


async def main_sites_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_add = types.InlineKeyboardButton(text='Добавить', callback_data='add-new-site')
    btn_delete = types.InlineKeyboardButton(text='Удалить', callback_data='delete-site')
    markup.inline_keyboard.append([btn_add, btn_delete])
    return markup


async def back_button(callback: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn = types.InlineKeyboardButton(text='Назад ◀️', callback_data=callback)
    markup.inline_keyboard.append([btn])
    return markup


async def yes_or_no_buttons(callback_prefix: str):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_yes = types.InlineKeyboardButton(text='Да', callback_data=f'{callback_prefix}_yes')
    btn_no = types.InlineKeyboardButton(text='Нет', callback_data=f'{callback_prefix}_no')
    markup.inline_keyboard.append([btn_yes, btn_no])
    return markup


async def pagination_sites(prefix_select: str, prefix_pagination: str, data: list, page: int, main_menu: bool):
    item_cnt = 2  # Кол-во объектов в одном блоке

    if (page < len(data) / item_cnt) and page >= 0:  # Проверка, что страница не последняя

        if len(data) % item_cnt > 0:  # Кол-во страниц
            all_pages = int(len(data) / item_cnt) + 1
        else:
            all_pages = int(len(data) / item_cnt)

        markup = types.InlineKeyboardMarkup(inline_keyboard=[])
        if len(data) <= item_cnt:
            for obj in data:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["url"], callback_data=f'{prefix_select}_{obj["id"]}')
                markup.inline_keyboard.append([btn])
        else:
            for obj in data[item_cnt * page: (item_cnt * page) + item_cnt]:
                obj = obj.__dict__
                btn = types.InlineKeyboardButton(text=obj["url"], callback_data=f'{prefix_select}_{obj["id"]}')
                markup.inline_keyboard.append([btn])

            btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'{prefix_pagination}_{page - 1}')
            btn_page = types.InlineKeyboardButton(text=f'Стр. {page + 1}/{all_pages}', callback_data=f'---')
            btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'{prefix_pagination}_{page + 1}')
            markup.inline_keyboard.append([btn_back, btn_page, btn_forward])

        if main_menu:
            btn_back = types.InlineKeyboardButton(text='Назад ◀️', callback_data='back-to-site-menu')
            markup.inline_keyboard.append([btn_back])
        else:
            btn_check = types.InlineKeyboardButton(text='Проверить все', callback_data='check-all-sites')
            markup.inline_keyboard.append([btn_check])

        return markup

    else:
        return None























