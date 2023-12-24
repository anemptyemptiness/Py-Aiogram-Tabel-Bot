from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Union


class CheckUserFilter(BaseFilter):

    def __init__(self, user_ids: list[Union[int, str]]):
        self.user_ids = user_ids

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) in self.user_ids
