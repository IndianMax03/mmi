import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import BotCommand, Message
from magic_filter import F

from analyser import Analyser
from auth import token

logging.basicConfig(level=logging.INFO)
bot = Bot(token)
dp = Dispatcher()
router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(
        'Привет, я бот, анализирующий двигательную активность.\n'
        'Напиши /help, для того, чтобы узнать, как со мной взаимодействовать!'
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        'Чтобы получить анализ вашей активности, достаточно отправить мне дневник самоконтроля в формате .csv'
    )


@router.message(F.content_type == 'document')
async def doc_handler(message: Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    created_filename = f'files/{message.from_user.id}-activity.csv'
    await bot.download_file(file_path, created_filename)
    await message.answer('Файл получен. Произвожу анализ...')
    analyser = Analyser(created_filename)
    await message.answer(f'Точность модели составляет: {analyser.get_accuracy()}%')
    await message.answer(analyser.get_attribute_impact_str())
    await message.answer(
        f'Если вы продолжите работать в том же духе и не перестанете уделять внимание параметру: "{analyser.get_main_impact_value_name()}", то за следующий месяц вам удастся сбросить {abs(analyser.get_weight_changing_in_moth()):.3f} кг!'
    )


dp.include_routers(
    router
)


async def setup_bot_commands():
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Запустить бота"),
            BotCommand(command="/help", description="Получить справку по работе бота"),
        ]
    )


async def main():
    await setup_bot_commands()
    logging.info("Starting bot")
    await dp.start_polling(bot)
    logging.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
