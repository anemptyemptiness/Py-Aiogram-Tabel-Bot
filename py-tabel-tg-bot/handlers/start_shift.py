from typing import Dict, Any
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from main import config
from fsm.fsm import FSMStartShift
from keyboards.reply_markup_kb import create_yes_no_kb, create_cancel_kb, create_places_kb
from middlewares.album_middleware import AlbumsMiddleware
from lexicon.lexicon_ru import LEXICON_RU
from filters.check_user import CheckUserFilter
from filters.check_chat import CheckChatFilter

router_start_shift = Router()
router_start_shift.message.middleware(middleware=AlbumsMiddleware(2))


async def report(dictionary: Dict[str, Any], date) -> str:
    return f"Дата: {date}\n" \
           f"Точка: {dictionary['place']}\n" \
           f"Имя: {dictionary['name']}\n" \
           f"Фото сотрудника: фото_1\n" \
           f"Видео сотрудника: видео_1\n" \
           f"Наличие дефектов: {'no' if dictionary['train_has_defects'] == 'no' else 'фото_2'}\n" \
           f"Проверка колёс: {dictionary['wheels_pumped']}\n" \
           f"Свет и подсветка на паровозе: {dictionary['train_flash']}\n" \
           f"Паровоз чистый: {dictionary['train_clean']}\n" \
           f"Магнитофон включен: {dictionary['is_recorder_on']}\n" \
           f"Томас включен: {dictionary['is_thomas_on']}"


@router_start_shift.message(CheckChatFilter(config.admin_chats))
async def warning_chat(message: Message):
    pass


@router_start_shift.message(CheckUserFilter(config.employees))
async def warning_user(message: Message):
    await message.answer(text="Вас нет в списке работников данной компании")


@router_start_shift.message(~StateFilter(default_state), F.text == "Отмена")
async def process_cancel_in_states_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Вы вернулись в главное меню',
                         reply_markup=ReplyKeyboardRemove())


@router_start_shift.message(StateFilter(default_state), F.text.startswith("/") == False)
async def warning_default(message: Message):
    await message.answer(text="Выберите нужную Вам команду из выпадающего меню")


@router_start_shift.message(Command(commands="start_shift"), StateFilter(default_state))
async def process_place_command(message: Message, state: FSMContext):
    await message.answer(text="Выберите точку, на которой Вы сейчас находитесь",
                         reply_markup=await create_places_kb())
    await state.set_state(FSMStartShift.place)


@router_start_shift.message(StateFilter(FSMStartShift.place), F.text)
async def process_start_shift_command(message: Message, state: FSMContext):
    await state.update_data(place=message.text)
    await message.answer(text="Пожалуйста, введите Ваше имя",
                         reply_markup=await create_cancel_kb())
    await state.set_state(FSMStartShift.my_name)


@router_start_shift.message(StateFilter(FSMStartShift.place))
async def warning_place_command(message: Message):
    await message.answer(text="Выберите рабочую точку ниже из выпадающего списка",
                         reply_markup=await create_cancel_kb())


@router_start_shift.message(StateFilter(FSMStartShift.my_name), F.text.isalpha())
async def process_get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Пожалуйста, отправьте Ваше фото на рабочем месте",
                         reply_markup=await create_cancel_kb())
    await state.set_state(FSMStartShift.my_photo)


@router_start_shift.message(StateFilter(FSMStartShift.my_name))
async def warning_get_name(message: Message):
    await message.answer(text="Вы ввели что-то некорректное\n\nВведите Ваше имя",
                         reply_markup=await create_cancel_kb())


@router_start_shift.message(StateFilter(FSMStartShift.my_photo))
async def process_get_photo(message: Message, state: FSMContext):
    if message.photo:  # получаю фото от пользователя
        await state.update_data(photo=message.photo[-1].file_id)
        await message.answer(text="Отлично, а теперь пришлите видео паровоза (в окружении)",
                             reply_markup=await create_cancel_kb())
        await state.set_state(FSMStartShift.my_video)
    else:
        await message.answer(text="Это не похоже на фото, попробуйте ещё раз",
                             reply_markup=await create_cancel_kb())


@router_start_shift.message(StateFilter(FSMStartShift.my_video))
async def process_get_video(message: Message, state: FSMContext):
    if message.video:
        await state.update_data(video=message.video.file_id)
        await message.answer(text="Отлично, а теперь я задам ряд вопросов, на которые Вам предстоит ответить!\n\n"
                                  "Проверьте паровоз на наличие дефектов. Есть ли дефекты?",
                             reply_markup=await create_yes_no_kb())
        await state.set_state(FSMStartShift.wait_for_defects)
    else:
        await message.answer(text="Это не похоже на видео, попробуйте еще раз",
                             reply_markup=await create_cancel_kb())


@router_start_shift.message(StateFilter(FSMStartShift.wait_for_defects), F.text == "Да")
async def process_defects_true(message: Message, state: FSMContext):
    await message.answer(text="Пришлите фото дефектов",
                         reply_markup=await create_cancel_kb())
    await state.set_state(FSMStartShift.photo_of_defects)


@router_start_shift.message(StateFilter(FSMStartShift.wait_for_defects), F.text == "Нет")
async def process_defects_false(message: Message, state: FSMContext):
    await state.update_data(train_has_defects="no")
    await message.answer(text="Вы проверили колёса у паровоза, достаточно ли они накачены?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.wheels)


@router_start_shift.message(StateFilter(FSMStartShift.wait_for_defects))
async def warning_process_defects(message: Message):
    await message.answer(text="Выберите ответ ниже на появившихся кнопках")


@router_start_shift.message(StateFilter(FSMStartShift.photo_of_defects))
async def process_need_to_photo_of_defects(message: Message, state: FSMContext):
    if message.photo:
        if 'train_has_defects' not in await state.get_data():
            await state.update_data(train_has_defects=[message.photo[-1].file_id])

        await message.answer(text="Вы проверили колёса у паровоза, достаточно ли они накачены?",
                             reply_markup=await create_yes_no_kb())
        await state.set_state(FSMStartShift.wheels)
    else:
        await message.answer(text="Это не похоже на фото, отправьте фото дефектов",
                             reply_markup=await create_cancel_kb())


@router_start_shift.message(StateFilter(FSMStartShift.wheels), F.text == "Да")
async def process_wheels_command_yes(message: Message, state: FSMContext):
    await state.update_data(wheels_pumped="yes")
    await message.answer(text="Включили ли Вы свет и подсветку на паровозе?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.train_flash)


@router_start_shift.message(StateFilter(FSMStartShift.wheels), F.text == "Нет")
async def process_wheels_command_no(message: Message, state: FSMContext):
    await state.update_data(wheels_pumped="no")
    await message.answer(text="Нужно подкачать колёса!\n\nВы включили свет и подсветку на паровозе?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.train_flash)


@router_start_shift.message(StateFilter(FSMStartShift.wheels))
async def warning_process_wheels(message: Message):
    await message.answer(text="Выберите ответ ниже на появившихся кнопках")


@router_start_shift.message(StateFilter(FSMStartShift.train_flash), F.text == "Да")
async def process_train_flash_command_yes(message: Message, state: FSMContext):
    await state.update_data(train_flash="yes")
    await message.answer(text="Вы протёрли паровоз от пыли?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.train_clean)


@router_start_shift.message(StateFilter(FSMStartShift.train_flash), F.text == "Нет")
async def process_train_flash_command_no(message: Message, state: FSMContext):
    await state.update_data(train_flash="no")
    await message.answer(text="Нужно включить подсветку!\n\nВы протёрли паровоз от пыли?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.train_clean)


@router_start_shift.message(StateFilter(FSMStartShift.train_flash))
async def warning_process_train_flash(message: Message):
    await message.answer(text="Выберите ответ ниже на появившихся кнопках")


@router_start_shift.message(StateFilter(FSMStartShift.train_clean), F.text == "Да")
async def process_train_clean_command_yes(message: Message, state: FSMContext):
    await state.update_data(train_clean="yes")
    await message.answer(text="Вы включили магнитофон?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.recorder)


@router_start_shift.message(StateFilter(FSMStartShift.train_clean), F.text == "Нет")
async def process_train_clean_command_no(message: Message, state: FSMContext):
    await state.update_data(train_clean="no")
    await message.answer(text="Нужно обязательно протереть паровоз!\n\nВы включили магнитофон?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.recorder)


@router_start_shift.message(StateFilter(FSMStartShift.recorder), F.text == "Да")
async def process_recorder_command_yes(message: Message, state: FSMContext):
    await state.update_data(is_recorder_on="yes")
    await message.answer(text="Вы включили Томас?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.thomas)


@router_start_shift.message(StateFilter(FSMStartShift.recorder), F.text == "Нет")
async def process_recorder_command_no(message: Message, state: FSMContext):
    await state.update_data(is_recorder_on="no")
    await message.answer(text="Вставьте флешку и включите!\n\nВы включили Томас?",
                         reply_markup=await create_yes_no_kb())
    await state.set_state(FSMStartShift.thomas)


@router_start_shift.message(StateFilter(FSMStartShift.recorder))
async def warning_process_train_clean(message: Message):
    await message.answer(text="Выберите ответ ниже на появившихся кнопках")


@router_start_shift.message(StateFilter(FSMStartShift.thomas), F.text == "Да")
async def process_thomas_command_yes(message: Message, state: FSMContext):
    await state.update_data(is_thomas_on="yes")
    await message.answer(text="Отлично! Отчёт сформирован... Отправляю начальству!",
                         reply_markup=ReplyKeyboardRemove())

    day_of_week = datetime.now().strftime('%A')
    current_date = datetime.now().strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

    start_shift_dict = await state.get_data()

    await message.bot.send_message(chat_id='-1002034135560',
                                   text=await report(start_shift_dict, current_date))
    await message.bot.send_photo(chat_id='-1002034135560',
                                 photo=start_shift_dict['photo'],
                                 caption='Фото сотрудника')
    await message.bot.send_video(chat_id='-1002034135560',
                                 video=start_shift_dict['video'],
                                 caption='Видео сотрудника')

    if start_shift_dict['train_has_defects'] != "no":
        media_defects = [InputMediaPhoto(media=photo_file_id,
                                         caption="Фото дефектов" if i == 0 else "")
                         for i, photo_file_id in enumerate(start_shift_dict['train_has_defects'])]

        await message.bot.send_media_group(chat_id='-1002034135560',
                                           media=media_defects)

    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.thomas), F.text == "Нет")
async def process_thomas_command_no(message: Message, state: FSMContext):
    await state.update_data(is_thomas_on="no")
    await message.answer(text="Надо включить!",
                         reply_markup=await create_cancel_kb())

    await message.answer(text="Отлично! Отчёт сформирован... Отправляю начальству!",
                         reply_markup=ReplyKeyboardRemove())

    day_of_week = datetime.now().strftime('%A')
    current_date = datetime.now().strftime(f'%d/%m/%Y - {LEXICON_RU[day_of_week]}')

    start_shift_dict = await state.get_data()

    await message.bot.send_message(chat_id='-1002034135560',
                                   text=await report(start_shift_dict, current_date))
    await message.bot.send_photo(chat_id='-1002034135560',
                                 photo=start_shift_dict['photo'],
                                 caption='Фото сотрудника')
    await message.bot.send_video(chat_id='-1002034135560',
                                 video=start_shift_dict['video'],
                                 caption='Видео сотрудника')

    if start_shift_dict['train_has_defects'] != "no":
        media_defects = [InputMediaPhoto(media=photo_file_id,
                                         caption="Фото дефектов" if i == 0 else "")
                         for i, photo_file_id in enumerate(start_shift_dict['train_has_defects'])]

        await message.bot.send_media_group(chat_id='-1002034135560',
                                           media=media_defects)

    await state.clear()


@router_start_shift.message(StateFilter(FSMStartShift.thomas))
async def warning_thomas_command(message: Message):
    await message.answer(text="Выберите ответ ниже из выпадающего списка!",
                         reply_markup=await create_yes_no_kb())
