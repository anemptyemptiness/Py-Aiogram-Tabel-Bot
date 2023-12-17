import asyncio

from config.config import load_config, redis
from handlers import start_shift, encashment, check_attractions, finish_shift
from menu_commands import set_default_commands

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

config = load_config()

bot = Bot(token=config.tg_bot.token)
storage = RedisStorage(redis=redis)
dp = Dispatcher(storage=storage)


async def main() -> None:
    # Подключаем роутеры к корневому роутеру (диспетчеру)
    dp.include_router(start_shift.router_start_shift)
    dp.include_router(encashment.router_encashment)
    dp.include_router(check_attractions.router_attractions)
    dp.include_router(finish_shift.router_finish)

    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
