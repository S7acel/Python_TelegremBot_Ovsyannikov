from calendar_class import Calendar
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from do_not_save_files.secrets import API_TOKEN

DETAILS, DATE, TIME, CREATE, READ_EVENT, DELETE_EVENT = range(6)

"""
Функции ask_event_details, ask_event_name, ask_event_date, ask_event_time -  спрашивают информацию у пользователя
и перенаправляют посредством ключей в словаре. Сам ключ - обозначает то, на какую функцию он перенаправляется
"""


def cancel(update, context):  # выход из функции
    update.message.reply_text("Создание события отменено")
    return ConversationHandler.END


def ask_event_name(update, context):
    update.message.reply_text(
        f"{update.message.from_user.username}, Напиши название события"
    )
    return DETAILS


def ask_event_details(update, context):
    context.chat_data["event_name"] = update.message.text
    update.message.reply_text(
        f'Напиши информацию события "{context.chat_data["event_name"]}"'
    )
    return DATE


def ask_event_date(update, context):
    context.chat_data["details"] = update.message.text
    update.message.reply_text(f"Напиши дату в формате дд/мм/гг")
    return TIME


def ask_event_time(update, context):
    context.chat_data["date"] = update.message.text
    update.message.reply_text(f"Теперь напиши время события в формате XX:XX")
    return CREATE


def create_event_handler(update, context):
    event_id = Calendar.create_event(
        context.chat_data["event_name"],
        context.chat_data["details"],
        context.chat_data["date"],
        update.message.text,
        update.message.chat_id,
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Событие {context.chat_data['event_name']} создано и имеет номер {event_id}.",
    )
    return ConversationHandler.END


def choose_event(update,context):
    context.chat_data["events_function"] = update.message.text
    if Calendar.return_user_events(update.message.chat_id):  # проверка на наличие событий
        context.chat_data["events"] = Calendar.return_user_events(update.message.chat_id)
        buttons = [[]]
        for d in context.chat_data['events']:
            buttons[0].append(f"{d[list(d.keys())[0]]['name']} ({list(d.keys())[0]})")  # добавление имён
        # Итерируемся по каждому событию - словарю в списке
        update.message.reply_text("Выберите событие:", reply_markup=ReplyKeyboardMarkup(
            buttons,
            one_time_keyboard=True))
        # в зависимости от выбранной команды - возвращается либо DELETE_EVENT, либо READ_EVENT
        return ConversationHandler.END

    else:
        update.message.reply_text("Событий - нет")
        return ConversationHandler.END


# прочтение выбранного, события
def read_event_handler(update, context):
    ReplyKeyboardRemove()
    event = update.message.text  # выбранное событие владельца
    id_of_event = event.split()[-1].strip('()')  # получение id из сообщения пользователя
    found_event = False
    for d in context.chat_data["events"]:  # итерация всех событий владельца
        if list(d.keys())[0] == id_of_event:
            update.message.reply_text(
                f"""
Id события: {list(d.keys())[0]}
Имя события: {d[id_of_event]["name"]}
детали события: {d[id_of_event]["details"]}
дата события: {d[id_of_event]['event_date']}
время события: {d[id_of_event]["event_time"]}
""",
                reply_markup=ReplyKeyboardRemove())
            found_event = True
            break
    if not found_event:
        update.message.reply_text("Такого события не существует.")
    return ConversationHandler.END


# итерация и показ всех событий пользователя посредством функции Calendar.return_user_events
def display_events(update, context):
    if Calendar.return_user_events(update.message.chat_id):
        context.chat_data["events"] = Calendar.return_user_events(update.message.chat_id)
        for d in context.chat_data['events']:
            update.message.reply_text(f"""
Id события: {list(d.keys())[0]}
Имя события: {list(d.values())[0]['name']}
детали события: {list(d.values())[0]["details"]}
дата события: {list(d.values())[0]['event_date']}
время события: {list(d.values())[0]["event_time"]}
""")

    else:
        update.message.reply_text("Событий - нет", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def delete_event_handler(update, context):
    ReplyKeyboardRemove()
    event = update.message.text  # выбранное имя событий владельца
    id_of_event = event.split()[-1].strip('()')  # получение id из сообщения пользователя
    result = Calendar.delete_user_events(update.message.chat_id, id_of_event)
    update.message.reply_text(f"{result}")
    return ConversationHandler.END


def edit_event_handler(update, context):
    ReplyKeyboardRemove()
    event = update.message.text  # выбранное имя событий владельца
    context.chat_data["id_of_event"] = event.split()[-1].strip('()')  # получение id из сообщения пользователя
    button_list = [
        InlineKeyboardButton('Имя', callback_data='name'),
        InlineKeyboardButton('детали', callback_data='details'),
        InlineKeyboardButton('дата', callback_data='event_date'),
        InlineKeyboardButton('время', callback_data='event_time')
    ]
    buttons = InlineKeyboardMarkup([button_list])
    update.message.reply_text(f"Выберите то, что хотите изменить",
                              reply_markup=buttons)  # добавит кнопку возле текста


conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("create", ask_event_name),
        CommandHandler("read", choose_event),
        CommandHandler('delete', choose_event),
        CommandHandler('edit', choose_event),
        CommandHandler('display', display_events),
    ],
    states={
        DETAILS: [MessageHandler(Filters.text & ~Filters.command, ask_event_details)],
        DATE: [MessageHandler(Filters.text & ~Filters.command, ask_event_date)],
        TIME: [MessageHandler(Filters.text & ~Filters.command, ask_event_time)],
        CREATE: [MessageHandler(Filters.text & ~Filters.command, create_event_handler)],

    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


# Обработчик нажатия на кнопку
def button_callback(update, context):
    query = update.callback_query
    context.chat_data["events_function"] = 'final_edit'
    if query.data == 'name':
        context.chat_data["data"] = query.data
        query.edit_message_text(f"Напиши новое имя события")
    elif query.data == 'details':
        context.chat_data["data"] = query.data
        query.edit_message_text(f"Напиши новые детали")
    elif query.data == 'event_date':
        context.chat_data["data"] = query.data
        query.edit_message_text(f"Напиши новую дату")
    elif query.data == 'event_time':
        context.chat_data["data"] = query.data
        query.edit_message_text(text='Напиши новое время')


# Создаем объект обработчика
button_handler = CallbackQueryHandler(button_callback)


def message_handler(update, context):
    if context.chat_data["events_function"] == '/read':
        read_event_handler(update, context)
        context.chat_data["events_function"] = ''
    elif context.chat_data["events_function"] == '/delete':
        delete_event_handler(update, context)
        context.chat_data["events_function"] = ''
    elif context.chat_data["events_function"] == '/edit':
        edit_event_handler(update, context)
        context.chat_data["events_function"] = ''
    elif context.chat_data["events_function"] == 'final_edit':
        result = Calendar.edit_user_events(update.message.chat_id, context.chat_data["id_of_event"],
                                           context.chat_data["data"],
                                           update.message.text)
        update.message.reply_text(f'{result}')
        context.chat_data["events_function"] = ''


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dispatcher.add_handler(button_handler)
    updater.start_polling()


if __name__ == "__main__":
    main()
