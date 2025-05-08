@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id != OWNER:
        return await message.answer("Добро пожаловать в бота поддержки! Здесь вы можете оставить вопрос или предложение.")
    else:
        return await message.answer("Добро пожаловать, босс. Наслаждайтесь использованием бота!")


@dp.message_handler(commands=['mute'])
async def mute(message: types.Message):
    if message.from_user.id == OWNER:
        replied_message = message.reply_to_message.text
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])
        name_of_user = replied_message.split()[4]

        banned_user = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id).count()
        if not banned_user:
            chat_id = BannedUsers(telegram_id=chat_id)
            session.add(chat_id)
            session.commit()
            return await message.answer(f"{name_of_user} добавлен в черный список")
        return await message.answer(f"{name_of_user} уже находится в черном списке")
    return await message.answer('У вас нет прав для этого действия!')


@dp.message_handler(commands=['unmute'])
async def unmute(message: types.Message):
    if message.from_user.id == OWNER:
        replied_message = message.reply_to_message.text
        chat_id = int(replied_message[replied_message.index('[') + 1:replied_message.index(']')])
        name_of_user = replied_message.split()[4]

        chat_id_query = session.query(BannedUsers).filter(BannedUsers.telegram_id == chat_id)
        if chat_id_query.count():
            chat_id_query.delete()
            session.commit()
            return await message.answer(f"{name_of_user} удалён из черного списка")
        return await message.answer(f'{name_of_user} не находится в черном списке')
    return await message.answer("У вас нет прав для этого действия!")


@dp.message_handler()
async def question_users(message: types.Message):
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
    return await message.answer("Вы добавлены в черный список и не можете писать этому боту.")
