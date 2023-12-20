import asyncio
import logging
from threading import Thread
from datetime import datetime, timedelta, timezone

import db
from config.config import config
from handlers import start_shift, encashment, check_attractions, finish_shift
from menu_commands import set_default_commands

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.token)
storage = RedisStorage(redis=config.redis)
dp = Dispatcher(storage=storage)
DB = db.db.DataBase(config=config)


async def auto_posting():
    while True:
        if (datetime.now(tz=timezone(timedelta(hours=3.0))).hour >= 10) \
                and (datetime.now(tz=timezone(timedelta(hours=3.0))).hour <= 20):

            await asyncio.sleep(60 * 30)

            user_ids = DB.get_users()

            for user_id in user_ids:
                try:
                    await bot.send_message(
                        chat_id=user_id[0],
                        text="⚠️ WARNING ⚠️"
                             "Пожалуйста, не забудьте сделать рекламный круг!"
                    )
                except Exception as e:
                    print("The user has blocked the bot:", e)
                    DB.set_active(
                        active=0,
                        user_id=user_id[0]
                    )


def creating_new_loop(global_loop):
    asyncio.run_coroutine_threadsafe(auto_posting(), global_loop)


async def main() -> None:
    # Подключаем роутеры к корневому роутеру (диспетчеру)
    dp.include_router(start_shift.router_start_shift)
    dp.include_router(encashment.router_encashment)
    dp.include_router(check_attractions.router_attractions)
    dp.include_router(finish_shift.router_finish)

    global_loop = asyncio.get_event_loop()
    auto_posting_thread = Thread(target=creating_new_loop, args=(global_loop,))
    auto_posting_thread.start()

    await set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
