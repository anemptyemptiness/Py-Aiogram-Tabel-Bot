from typing import Union
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from fsm.fsm import FSMEncashment
from lexicon.lexicon_ru import LEXICON_RU
from keyboards.reply_markup_kb import create_cancel_kb, create_places_kb
from middlewares.album_middleware import AlbumsMiddleware

router_encashment = Router()
router_encashment.message.middleware(middleware=AlbumsMiddleware(2))


async def report(dictionary: dict, date):
    return f"Точка: {dictionary['place']}\n" \
           f"Дата: {date}\n\n" \
           f"Дата инкассации: {dictionary['date']}\n" \
           f"Сумма инкассации: {dictionary['summary']}\n"


@router_encashment.message(Command(commands="encashment"), StateFilter(default_state))
async def process_place_command(message: Message, state: FSMContext):
    await state.set_state(FSMEncashment.place)
    await message.answer(text="Выберите точку, на которой Вы сейчас находитесь",
                         reply_markup=await create_places_kb())


@router_encashment.message(StateFilter(FSMEncashment.place), F.text)
async def process_photo_of_check_command(message: Message, state: FSMContext):
    await state.update_data(place=message.text)
    await message.answer(text="Пожалуйста, пришлите сюда фото чека инкассации\n\n"
                              "Если инкассации нет, напишите 0",
                         reply_markup=await create_cancel_kb())
    await state.set_state(FSMEncashment.photo_of_check)


@router_encashment.message(StateFilter(FSMEncashment.place))
async def warning_place_command(message: Message):
    await message.answer(text="Выберите рабочую точку ниже из выпадающего списка",
                         reply_markup=await create_cancel_kb())


@router_encashment.message(StateFilter(FSMEncashment.photo_of_check))
async def process_wait_for_check_command(message: Message, state: FSMContext):
    if message.photo:
        if 'photo_of_check' not in await state.get_data():
            await state.update_data(photo_of_check=[message.photo[-1].file_id])

        await message.answer(text="Отлично, а теперь пришлите сумму инкассации числом",
                             reply_markup=await create_cancel_kb())
        await state.set_state(FSMEncashment.summary)
    elif message.text == "0":
        await state.update_data(photo_of_check="0")

        encashment_dict = await state.get_data()
        encashment_dict['summary'] = "0"
        encashment_dict['date'] = "None"

        day_of_week = datetime.now().strftime('%A')
        date = datetime.now().strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

        await message.bot.send_message(chat_id='-1002034135560',
                                       text=await report(encashment_dict, date=date))

        await message.answer(text="Отлично, все данные отправлены начальству!",
                             reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer(text="Введите 0 или отправьте фото чека!",
                             reply_markup=await create_cancel_kb())


@router_encashment.message(StateFilter(FSMEncashment.photo_of_check))
async def warning_wait_for_check_command(message: Message):
    await message.answer(text="Пришлите фото чека или 0, если инкассации не было!",
                         reply_markup=await create_cancel_kb())


@router_encashment.message(StateFilter(FSMEncashment.summary), F.text.isdigit())
async def process_wait_for_summary_command(message: Message, state: FSMContext):
    await state.update_data(summary=int(message.text))
    await message.answer(text="Отлично, а теперь пришлите дату, за которую делали инкассацию",
                         reply_markup=await create_cancel_kb())
    await state.set_state(FSMEncashment.date_of_cash)


@router_encashment.message(StateFilter(FSMEncashment.summary))
async def warning_wait_for_summary_command(message: Message):
    await message.answer(text="Пришлите сумму числом!",
                         reply_markup=await create_cancel_kb())


@router_encashment.message(StateFilter(FSMEncashment.date_of_cash), F.text)
async def process_wait_for_date_command(message: Message, state: FSMContext):
    await state.update_data(date=message.text)

    encashment_dict = await state.get_data()

    day_of_week = datetime.now().strftime('%A')
    date = datetime.now().strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

    await message.bot.send_message(chat_id='-1002034135560',
                                   text=await report(encashment_dict, date=date))

    if not isinstance(encashment_dict['photo_of_check'], str):
        media_check = [InputMediaPhoto(media=photo_file_id,
                                       caption="Фото чека инкассации" if i == 0 else "")
                               for i, photo_file_id in enumerate(encashment_dict['photo_of_check'])]
        await message.bot.send_media_group(chat_id="-1002034135560",
                                           media=media_check)

        # await message.bot.send_photo(chat_id='-1002034135560',
        #                              photo=encashment_dict['photo_of_check'],
        #                              caption="Фото чека инкассации")
    await message.answer(text="Отлично, все данные отправлены начальству!",
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router_encashment.message(StateFilter(FSMEncashment.date_of_cash))
async def warning_wait_for_date_command(message: Message):
    await message.answer(text="Отправьте дату инкассации!",
                         reply_markup=await create_cancel_kb())
