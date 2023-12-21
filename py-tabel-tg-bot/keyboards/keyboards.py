from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup


async def create_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
        [KeyboardButton(text="Отмена")]
    ]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True)


async def create_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Отмена")]
    ]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True)


async def create_places_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Щелковский")],
        [KeyboardButton(text="Белая Дача")],
        [KeyboardButton(text="Ривьера")],
        [KeyboardButton(text="Вегас Кунцево")],
        [KeyboardButton(text="Рига Молл")],
    ]

    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True)


async def create_inline_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(
            text="Согласен",
            callback_data="agree")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)
