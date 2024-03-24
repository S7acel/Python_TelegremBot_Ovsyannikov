"""Импорт апи токена, класса Calendar, и необходимых функций для обработки сообщений"""
from secrets import API_TOKEN
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler
)
from calendar_class import Calendar
from message_texts import *

(NAME, DETAILS, DATE, TIME, READ_EVENT, CHOOSE_EVENT, EDIT_OBJECT,
 NEW_EDIT_OBJECT, ANSWER, REQUIRED_TEXT_FOR_CHANGE) = range(10)

"""
Функции ask_event_details, ask_event_name, ask_event_date, ask_event_time -
спрашивают информацию у пользователя
и перенаправляют посредством ключей в словаре.
Сам ключ - обозначает то, на какую функцию он перенаправляется
"""


def start(update, context):
    """Приветственный текст, весь функционал"""
    (update.message.reply_text(GREETINGS, parse_mode='markdown'))


def cancel(update, _context):
    """При использовании этой команды, пользователь отменяет диалог с командами"""
    update.message.reply_text(CANCELLING)
    return ConversationHandler.END


def ask_event_name(update, _context):
    """Спрашивание названия события"""
    update.message.reply_text(
        f'{update.message.from_user.first_name} {ASK_FOR_EVENT}'
    )
    return NAME


def ask_event_details(update, context):
    """Спрашивание деталей, информации события"""
    context.chat_data["event_name"] = update.message.text
    update.message.reply_text(
        f'Напиши информацию события "{context.chat_data["event_name"]}"'
    )
    return DETAILS


def ask_event_date(update, context):
    """Спрашивание даты события"""
    context.chat_data["details"] = update.message.text
    update.message.reply_text(ASK_DATE)
    return DATE


def ask_event_time(update, context):
    """Спрашивание времени события"""
    context.chat_data["date"] = update.message.text
    update.message.reply_text(ASK_TIME)
    return TIME


def create_event_handler(update, context):
    """После спрашивания всей необходимой информации,
    используется метод для создания события в классе Calendar.
    Информация записывается в файл с помощью метода create_and_add_event_to_file"""
    Calendar.write_user_in_table(update.message.chat_id,
                                 update.message.from_user.first_name,
                                 update.message.from_user.username)
    result = Calendar.add_event_to_database(context.chat_data["event_name"],
                                            context.chat_data["details"],
                                            context.chat_data["date"], update.message.text,
                                            update.message.chat_id)
    update.message.reply_text(result)
    return ConversationHandler.END


def choose_event(update, context):
    """В этой функции, мы используем метод return_user_events.
    Он в свою очередь, возвращает события пользователя.
    После этого мы создаем кнопки события в формате
    'ИМЯ (ID)'"""
    context.chat_data["events_function"] = update.message.text
    if Calendar.check_exists_of_objects(update.message.chat_id):
        events = Calendar.return_user_events(update.message.chat_id)
        keyboard = [[]]
        for event in events:  # Итерируемся по каждому событию - словарю в списке
            id_of_event = event[0]
            name = event[1]
            keyboard[0].append(InlineKeyboardButton(f"{name} ({id_of_event})",
                                                    callback_data=id_of_event))  # добавление кнопок
        update.message.reply_text(CHOSE_EVENT, reply_markup=InlineKeyboardMarkup(
            keyboard))
        return CHOOSE_EVENT
    update.message.reply_text("Событий - нет")
    return ConversationHandler.END


def read_event_handler(update, context):
    """Вывод выбранного события на экран."""
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    event_id = context.user_data['event_id']
    event = Calendar.return_user_events(chat_id,
                                        event_id)[0]
    query.edit_message_text(f"id события: {event[0]}\nимя события: {event[1]}\nдетали события: {event[2]}\n"
                            f"дата: {event[3]}\nвремя события {event[4]}")
    return ConversationHandler.END


def do_action(update, context):
    """В этой функции, в зависимости от команды,
    выполняется действие в match_case"""
    query = update.callback_query
    query.answer()
    context.user_data['event_id'] = query.data

    match context.chat_data["events_function"].lower():
        case "/read":
            return read_event_handler(update, context)
        case "/edit":
            return ask_edit_object(update, context)
        case "/delete":
            return delete_event(update, context)
    return ConversationHandler.END


def display_events(update, context):
    """Итерация и показ всех событий"""
    all_events = Calendar.return_user_events(update.message.chat_id)
    if all_events:

        for event in all_events:
            update.message.reply_text(f"""
Id события: {event[0]}
Имя события: {event[1]}
детали события: {event[2]}
дата события: {event[3]}
время события: {event[4]}
""")
        return ConversationHandler.END

    update.message.reply_text("Событий - нет", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def delete_event(update, context):
    """Удаление события за счет метода delete_user_events."""
    query = update.callback_query
    query.answer()
    result = Calendar.delete_user_events(query.message.chat_id, context.user_data['event_id'])
    query.edit_message_text(f"{result}")
    return ConversationHandler.END


def ask_edit_object(update, context):
    """Функция спрашивает, что конкретно хотим изменить. Так """
    query = update.callback_query
    query.answer()
    buttons = [
        [
            InlineKeyboardButton('имя', callback_data='event_name'),
            InlineKeyboardButton('детали', callback_data='event_details')
        ],
        [
            InlineKeyboardButton('дату', callback_data='event_date'),
            InlineKeyboardButton('время', callback_data='event_time')
        ]
    ]

    query.edit_message_text("Что вы хотите изменить?", reply_markup=InlineKeyboardMarkup(
        buttons))
    return EDIT_OBJECT


def ask_for_write_new_text(update, context):
    """Далее, после спрашивания, о том какое объект изменяем,
    Спрашиваем на какой текст мы хотим изменить"""
    query = update.callback_query
    query.answer()
    query.edit_message_text('Введите новое сообщение для изменения:')
    context.user_data['option'] = query.data
    return NEW_EDIT_OBJECT


def edit_event(update, context):
    """После получения всей необходимой информации, используем функцию
    edit_user_events для редактирования события, так же с целью безопастности делается
     проверка на принадлежность к событию перед редактированием"""
    event_id = context.user_data['event_id']
    if Calendar.check_exists_of_objects(update.message.chat_id, event_id):
        result = Calendar.edit_user_events(update.message.chat_id, event_id,
                                           context.user_data['option'], update.message.text)
        update.message.reply_text(f'{result}')
    else:
        update.message.reply_text('Произошла ошибка. Данное событие не принадлежит вам!')
    return ConversationHandler.END


def delete_all_events(update, context):
    """Спрашивание об удалении всех заметок"""
    update.message.reply_text("""*Вы уверены?*
Да-'Y'/Нет-'N'
""", parse_mode='Markdown')
    return ANSWER


def check_chose_to_delete(update, context):
    """В зависимости от сообщения - удаление файлов
    (С помощью итерации событий через delete_user_events)"""
    chose = update.message.text
    if chose.lower() == 'y':
        all_events = Calendar.return_user_events(update.message.chat_id)
        if all_events:  # проверка на наличие событий
            for event in all_events:
                id_of_event = event[0]
                result = Calendar.delete_user_events(update.message.chat_id, id_of_event)
                update.message.reply_text(f"{result}")
            update.message.reply_text("*Все события удалены успешно!*", parse_mode='markdown')
            return ConversationHandler.END
        update.message.reply_text("Событий - нет")
        return ConversationHandler.END
    return cancel(update, context)



conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("read", choose_event),
        CommandHandler('delete', choose_event),
        CommandHandler('edit', choose_event),
        CommandHandler('display', display_events),
        CommandHandler('delete_all', delete_all_events),
    ],
    states={
        CHOOSE_EVENT: [CallbackQueryHandler(do_action)],
        EDIT_OBJECT: [CallbackQueryHandler(ask_for_write_new_text)],
        NEW_EDIT_OBJECT: [MessageHandler(Filters.text & ~Filters.command, edit_event)],
        ANSWER: [MessageHandler(Filters.text & ~Filters.command, check_chose_to_delete)]

    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False
)

create_handler = ConversationHandler(
    entry_points=[
        CommandHandler("create", ask_event_name)
    ],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, ask_event_details)],
        DETAILS: [MessageHandler(Filters.text & ~Filters.command, ask_event_date)],
        DATE: [MessageHandler(Filters.text & ~Filters.command, ask_event_time)],
        TIME: [MessageHandler(Filters.text & ~Filters.command, create_event_handler)]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)


def main():
    """Создание обработчика conversation handler, запуск бота"""
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(create_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()


if __name__ == "__main__":
    main()
