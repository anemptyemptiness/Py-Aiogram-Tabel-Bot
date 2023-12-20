from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import db
from fsm.fsm import FSMAdmin
from filters.is_admin import isAdminFilter
from config.config import config

router_adm = Router()


@router_adm.message(Command(commands="stats"), isAdminFilter(config.admins))
async def process_get_stats_command(message: Message, state: FSMContext):
    await state.set_state(FSMAdmin.stats)
    await message.answer(text="Введите дату в таком формате <em>Год-месяц-день</em>\n\n"
                              "Например: 2023-12-20, что означает 12 декабря 2023 года\n\n"
                              "Если цифра дня меньше 10, то вводите день вот так <em>01-09</em>\n"
                              "Например, 2023-12-<b>01</b>, что означает 1 декабря 2023 года",
                         parse_mode="html")


@router_adm.message(isAdminFilter(config.admins), StateFilter(FSMAdmin.stats), F.text)
async def get_stats(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

    rows = db.DB.get_statistics(message.text)
    for i in range(len(rows)):
        await message.answer(text="Статистика по количеству посетителей за день "
                                  f"за {(await state.get_data())['date']}\n\n"
                                  f"Дата: {rows[i][3]}\n"
                                  f"Точка: {rows[i][2]}\n"
                                  f"Имя: {rows[i][1]}\n\n"
                                  f"Количество посетителей: {rows[i][0]}")
    await state.clear()


@router_adm.message(isAdminFilter(config.admins))
async def warning_get_stats(message: Message):
    await message.answer(text="Введите дату в таком формате <em>Год-месяц-день</em>\n\n"
                              "Например: 2023-12-20, что означает 12 декабря 2023 года\n\n"
                              "Если цифра дня меньше 10, то вводите день вот так <em>01-09</em>\n"
                              "Например, 2023-12-<b>01</b>, что означает 1 декабря 2023 года",
                         parse_mode="html")
