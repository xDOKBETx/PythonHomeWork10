import phonebook_model
from bot_token import token as TOKEN
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

_user = {}


def run():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('all', all_users))
    dispatcher.add_handler(CommandHandler('help', help_info))

    add_user_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_user)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, set_first_name)],
            2: [MessageHandler(Filters.text & ~Filters.command, set_last_name)],
            3: [MessageHandler(Filters.text & ~Filters.command, set_phone)],
            4: [MessageHandler(Filters.text & ~Filters.command, set_description)],
        },
        fallbacks=[CommandHandler('stop', stop_operation)]
    )
    dispatcher.add_handler(add_user_handler)

    del_user_handler = ConversationHandler(
        entry_points=[CommandHandler('del', del_user)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, del_user_set_id)],
        },
        fallbacks=[CommandHandler('stop', stop_operation)]
    )
    dispatcher.add_handler(del_user_handler)

    search_user_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search_user)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, search_user_set_filter)],
        },
        fallbacks=[CommandHandler('stop', stop_operation)]
    )
    dispatcher.add_handler(search_user_handler)

    updater.start_polling()
    updater.idle()


def start(update, context):
    context.bot.send_message(update.effective_chat.id, "Привет! Добро пожаловать в телефонный справочник.")


def all_users(update, context):
    users = phonebook_model.get_all_users()
    if len(users) == 0:
        context.bot.send_message(update.effective_chat.id, "Список пуст")
        return

    result = users_to_str(users)
    context.bot.send_message(update.effective_chat.id, result)


def help_info(update, context):
    result = "/all - выводит все контакты\n"
    result += "/add - добавляет новый контакт\n"
    result += "/del - удаляет контакт по id\n"
    result += "/search - ищет контакт по фамилии\n"
    result += "/stop - отменяет начатую операцию"
    context.bot.send_message(update.effective_chat.id, result)


def users_to_str(users: [{}]):
    result = ""
    for u in users:
        result += f'{u["id"]}. {u["first_name"]} {u["last_name"]}: {u["phone"]} ({u["description"]})\n'
    return result


# ============== ADD USER ==============
def add_user(update, context):
    global _user
    _user = {}
    update.message.reply_text("Укажите имя")
    return 1


def stop_operation(update, context):
    update.message.reply_text("Операция отменена")
    return ConversationHandler.END


def set_first_name(update, context):
    global _user
    _user["first_name"] = update.message.text
    update.message.reply_text("Укажите фамилию")
    return 2


def set_last_name(update, context):
    global _user
    _user["last_name"] = update.message.text
    update.message.reply_text("Укажите телефон")
    return 3


def set_phone(update, context):
    global _user
    _user["phone"] = update.message.text
    update.message.reply_text("Укажите описание")
    return 4


def set_description(update, context):
    global _user
    _user["description"] = update.message.text
    phonebook_model.add_user(_user)
    update.message.reply_text("Контакт успешно добавлен!")
    return ConversationHandler.END


# ============== DELETE USER ==============
def del_user(update, context):
    update.message.reply_text("Укажите id")
    return 1


def del_user_set_id(update, context):
    try:
        user_id = int(update.message.text)
        phonebook_model.delete_user(user_id)
        update.message.reply_text("Контакт успешно удалён!")
    except ValueError:
        update.message.reply_text("Ошибка: некорретный формат числа")

    return ConversationHandler.END


# ============== SEARCH USER ==============
def search_user(update, context):
    update.message.reply_text("Введите строку поиска")
    return 1


def search_user_set_filter(update, context):
    search_str = update.message.text
    users = phonebook_model.search_users(search_str)

    if len(users) == 0:
        update.message.reply_text("Ничего не нашлось")
        return

    result = users_to_str(users)
    update.message.reply_text(result)
    return ConversationHandler.END
