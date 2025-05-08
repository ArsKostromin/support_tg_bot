import logging

from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN, OWNER
from functions import edit_message
from models import BannedUsers, session

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Приветственное сообщение для пользователей и владельца.
    """
    if message.from_user.id != OWNER:
        return await message.answer("Добро пожаловать в бота поддержки! Здесь вы можете оставлять вопросы и предложения.")
    else:
        return await message.answer("Добро пожаловать, босс. Приятного использования бота!")


@dp.message_handler(commands=['mute'])
async def mute(message: types.Message):
    """
    Эта функция блокирует пользователя, добавляя его в чёрный список.
    Работает только для владельца бота.
    """
    if message.from_user.id == OWNER:
        replied_message = message.reply_to_message.text
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])
        name_of_user = replied_message.split()[4]

        banned_user = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id).count()
        if not banned_user:
            chat_id = BannedUsers(telegram_id=chat_id)
            session.add(chat_id)
            session.commit()
            return await message.answer(f"{name_of_user} добавлен в чёрный список.")
        return await message.answer(f"{name_of_user} уже находится в чёрном списке.")
    return await message.answer("У вас нет прав для выполнения этой команды!")


@dp.message_handler(commands=['unmute'])
async def unmute(message: types.Message):
    """
    Эта функция разблокирует пользователя, удаляя его из чёрного списка.
    Работает только для владельца бота.
    """
    if message.from_user.id == OWNER:
        replied_message = message.reply_to_message.text
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])
        name_of_user = replied_message.split()[4]

        chat_id_query = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id)
        if chat_id_query.count():
            chat_id_query.delete()
            session.commit()
            return await message.answer(f"{name_of_user} удалён из чёрного списка.")
        return await message.answer(f"{name_of_user} не найден в чёрном списке.")
    return await message.answer("У вас нет прав для выполнения этой команды!")


@dp.message_handler()
async def question_users(message: types.Message):
    """
    Эта функция пересылает сообщения от пользователей владельцу бота,
    и наоборот (если сообщение является ответом).
    """
    if message.from_user.id == OWNER:
        if not message.reply_to_message:
            return await message.answer("Ваше сообщение должно быть ответом на пересланное сообщение!")
        replied_message = message.reply_to_message.text
        chat_id = replied_message[replied_message.index('[') + 1:replied_message.index(']')]
        return await bot.send_message(chat_id, message.text)

    user_id = message.from_user.id

    if not session.query(BannedUsers).filter(BannedUsers.telegram_id == user_id).count():
        edited_message = edit_message(message)
        return await bot.send_message(OWNER, edited_message)
    return await message.answer("Вы внесены в чёрный список этого бота.")
    

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
