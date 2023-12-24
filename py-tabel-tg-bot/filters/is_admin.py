from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Union


class isAdminFilter(BaseFilter):
    def __init__(self, admin_ids: list[Union[str, int]]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) in self.admin_ids
