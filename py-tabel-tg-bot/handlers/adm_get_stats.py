import logging

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
    await message.answer(text="Введите диапазон дат <b>ЧЕРЕЗ ПРОБЕЛ</b>"
                              " в таком формате: <em>Год-месяц-день Год-месяц-день</em>\n\n"
                              'Например: 2023-12-20 2023-12-21, '
                              'что означает от 20 декабря 2023 года до 21 декабря 2023 года\n\n'
                              "Если цифра дня меньше 10, то вводите день вот так: <em>01-09</em>\n\n"
                              'Например, 2023-12-<b>01</b> 2023-12-<b>02</b>, '
                              'что означает от 1 декабря 2023 года до 2 декабря 2023 года',
                         parse_mode="html")


@router_adm.message(isAdminFilter(config.admins), StateFilter(FSMAdmin.stats), F.text)
async def get_stats(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

    date_from, date_to = (await state.get_data())['date'].split()

    try:
        rows = db.DB.get_statistics(date_from=date_from, date_to=date_to)

        places = {
            "Белая Дача": sum([row[0].count("Белая Дача") for row in rows]),
            "Ривьера": sum([row[0].count("Ривьера") for row in rows]),
            "Рига Молл": sum([row[0].count("Рига Молл") for row in rows]),
            "Вегас Кунцево": sum([row[0].count("Вегас Кунцево") for row in rows]),
            "Щелковский": sum([row[0].count("Щелковский") for row in rows]),
        }

        report = f"📊Статистика по посетителям точек\n<b>от</b> {date_from} <b>до</b> {date_to}\n\n"
        index_place = 0
        index_rows = 0

        for count in places.values():
            if count:
                report += f"Рабочая точка: <b>{rows[index_place][0]}</b>\n"

                for i in range(count):
                    report += f"📝Работник: <em>{rows[index_rows][1]}</em>\n└"
                    report += f"посетителей: <em>{rows[index_rows][2]}</em>\n\n"

                    index_rows += 1

                report += "\n"
                index_place += count

        await message.answer(text=report,
                             parse_mode="html")

    except Exception as e:
        await message.bot.send_message(text=f"Get stats error: {e}\n"
                                            f"User_id: {message.from_user.id}",
                                       chat_id=config.admins[0])
        await message.answer(text="⚠️ ВНИМАНИЕ ⚠️\n\n"
                                  "Возникла <b>ошибка</b> при сборе данных, "
                                  "проверьте правильность введенных значений и повторите команду",
                             parse_mode="html")
    finally:
        await state.clear()


@router_adm.message(isAdminFilter(config.admins), StateFilter(FSMAdmin.stats))
async def warning_get_stats(message: Message):
    await message.answer(text="Введите дату в таком формате: <em>Год-месяц-день</em> через пробел\n\n"
                              'Например: 2023-12-20 2023-12-21\n\n'
                              "Если цифра дня меньше 10, то вводите день вот так: <em>01-09</em>\n"
                              'Например, 2023-12-<b>01</b> 2023-12-<b>02</b>',
                         parse_mode="html")
