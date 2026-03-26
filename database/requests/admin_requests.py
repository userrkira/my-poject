from database.models import async_session, Sites
from sqlalchemy import select, or_, and_, delete, func, case, cast, Integer, String
import logging


async def add_new_site(url: str) -> None:
    """Добавление нового сайта"""
    logging.info('add_new_site')
    async with async_session() as session:
        new_site = Sites(url=url)
        session.add(new_site)
        await session.commit()


async def delete_site(url: int) -> None:
    """Удаление сайта"""
    logging.info('delete_site')
    async with async_session() as session:
        site = await session.scalar(select(Sites).where(Sites.url == url))
        await session.delete(site)
        await session.commit()


async def get_all_sites() -> list:
    """Получение списка всех чатов"""
    logging.info('get_all_sites')
    async with async_session() as session:
        sites = await session.scalars(select(Sites))
        if sites:
            return sites.all()
        else:
            return []


async def get_site_by_id(id_: int) -> str:
    """получение url сайта по id"""
    logging.info('get_site_by_id')
    async with async_session() as session:
        site = await session.scalar(select(Sites.url).where(Sites.id == id_))
        return site