"""Импорт апи токена, класса Calendar, и необходимых функций для обработки сообщений"""
from secrets import API_TOKEN
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
)
from calendar_class import Calendar

(DETAILS, DATE, TIME, CREATE, READ_EVENT, CHECK_EXIST, ASK_FOR_CHANGE,
 EDIT_EVENT, CHOOSE_TO_DELETE) = range(9)

"""
Функции ask_event_details, ask_event_name, ask_event_date, ask_event_time -
спрашивают информацию у пользователя
и перенаправляют посредством ключей в словаре.
Сам ключ - обозначает то, на какую функцию он перенаправляется
"""



def start(update, context):
    """Приетственный текст, весь функционал"""
    (update.message.reply_text("""
*Привет!* Я бот, который поможет тебе создавать, редактировать, удалять и просматривать события. 

Для создания нового события используй команду */create*. Чтобы просмотреть все свои события, используй команду */display*. Чтобы удалить все свои события, используй команду */delete_all*. Чтобы удалить конкретное событие, используй команду */delete*. Чтобы отредактировать событие, используй команду */edit*. Чтобы прочитать информацию о конкретном событии, используй команду */read*.

Надеюсь, я смогу помочь тебе в управлении твоими событиями! 🤖

""", parse_mode='markdown'))

def cancel(update, _context):
    """При использовании этой команды, пользователь отменяет диалог с командами"""
    update.message.reply_text("Создание события отменено")
    return ConversationHandler.END


def ask_event_name(update, _context):
    """Спрашивание названия события"""
    update.message.reply_text(
        f"{update.message.from_user.username}, Напиши название события"
    )
    return DETAILS


def ask_event_details(update, context):
    """Спрашивание деталей, информации события"""
    context.chat_data["event_name"] = update.message.text
    update.message.reply_text(
        f'Напиши информацию события "{context.chat_data["event_name"]}"'
    )
    return DATE


def ask_event_date(update, context):
    """Спрашивание даты события"""
    context.chat_data["details"] = update.message.text
    update.message.reply_text("Напиши дату в формате дд/мм/гг")
    return TIME


def ask_event_time(update, context):
    """Спрашивание времени события"""
    context.chat_data["date"] = update.message.text
    update.message.reply_text("Теперь напиши время события в формате XX:XX")
    return CREATE


def create_event_handler(update, context):
    """После спрашивания всей необходимой информации,
    используется метод для создания события в классе Calendar.
    Информация записывается в файл events.json"""
    event_data = {'event_name': context.chat_data["event_name"],
                  'details': context.chat_data["details"],
                  'event_date': context.chat_data["date"],
                  'event_time': update.message.text,
                  'chat_id': update.message.chat_id}
    event_id = Calendar.create_and_add_event_to_file(context.chat_data["event_name"],context.chat_data["details"],
                                                     context.chat_data["date"], update.message.text,
                                                     update.message.chat_id)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Событие {context.chat_data['event_name']} создано с номером {event_id}.",

    )
    return ConversationHandler.END


def choose_event(update, context):
    """В этой функции, мы используем метод return_user_events.
    Он в свою очередь, возвращает события пользователя.
    После этого мы создаем кнопки события в формате
    'ИМЯ (ID)'"""
    context.chat_data["events_function"] = update.message.text
    if Calendar.return_user_events(update.message.chat_id):  # проверка на наличие событий
        context.chat_data["all_events"] = Calendar.return_user_events(update.message.chat_id)
        buttons = [[]]
        for event in context.chat_data['all_events']:
            name = event[list(event.keys())[0]]['name']
            id_of_event = list(event.keys())[0]
            buttons[0].append(f"{name} ({id_of_event})")  # добавление имён
        # Итерируемся по каждому событию - словарю в списке
        update.message.reply_text("Выберите событие:", reply_markup=ReplyKeyboardMarkup(
            buttons,
            one_time_keyboard=True))
        return CHECK_EXIST
    update.message.reply_text("Событий - нет")
    return ConversationHandler.END


def check_exist_of_event(update, context):
    """В этой функции проверяется существовани данного события.
    В случае неправильного написания, словарь не найдется в списке
    и отправится сообщени о его несуществовании.
    Так же в этой функции, происходит переход на другую функцию,
     в зависимости от команды"""
    ReplyKeyboardRemove()
    event = update.message.text
    event_id = event.split()[-1].strip('()')  # получение id из сообщения пользователя
    found_event = False
    for dict_event in context.chat_data["all_events"]:  # итерация всех событий владельца
        if list(dict_event.keys())[0] == event_id:
            found_event = True
            context.chat_data["event"] = dict_event  # добавление выбранного события в словарь
            break
    if not found_event:
        update.message.reply_text("Такого события не существует.")
        return ConversationHandler.END

    match context.chat_data["events_function"].lower():
        case "/read":
            return read_event_handler(update, context)
        case "/edit":
            return edit_event_handler(update, context)
        case "/delete":
            return delete_event_handler(update, context)


def read_event_handler(update, context):
    """Вывод выбранного события на экран."""
    event = context.chat_data['event']
    event_id = list(event.keys())[0]
    update.message.reply_text(f"""
id: {event_id}
Имя: {event[event_id]['name']}
Детали: {event[event_id]['details']}
Дата: {event[event_id]['event_date']}
Время: {event[event_id]['event_time']}
""")
    return ConversationHandler.END


def display_events(update, context):
    """Итерация и показ всех событий пользователся"""
    if Calendar.return_user_events(update.message.chat_id):
        context.chat_data["all_events"] = Calendar.return_user_events(update.message.chat_id)
        for d in context.chat_data['all_events']:
            update.message.reply_text(f"""
Id события: {list(d.keys())[0]}
Имя события: {list(d.values())[0]['name']}
детали события: {list(d.values())[0]["details"]}
дата события: {list(d.values())[0]['event_date']}
время события: {list(d.values())[0]["event_time"]}
""")
        return ConversationHandler.END

    update.message.reply_text("Событий - нет", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def delete_event_handler(update, context):
    """Удаление события за счет метода delete_user_events."""
    event = context.chat_data['event']
    event_id = list(event.keys())[0]
    result = Calendar.delete_user_events(update.message.chat_id, event_id)
    update.message.reply_text(f"{result}")
    return ConversationHandler.END


def edit_event_handler(update, context):
    """Функция спрашивает, что конкретно хотим изменить."""
    ReplyKeyboardRemove()
    buttons = [['имя', 'детали', 'дата', 'время']]

    update.message.reply_text("Что вы хотите изменить?", reply_markup=ReplyKeyboardMarkup(
        buttons,
        one_time_keyboard=True))  # добавит кнопку возле текста
    return ASK_FOR_CHANGE


def ask_for_write_new_text(update, context):
    """Далее, после спрашивания, о том какое объект изменяем,
    Спрашиваем на какой текст мы хотим изменить"""
    update.message.reply_text('Напишите новый текст', reply_markup=ReplyKeyboardRemove())
    match update.message.text:
        case 'имя':
            context.chat_data['edit_object'] = 'name'
        case 'детали':
            context.chat_data['edit_object'] = 'details'
        case 'дата':
            context.chat_data['edit_object'] = 'event_date'
        case 'время':
            context.chat_data['edit_object'] = 'event_time'
        case _:
            update.message.reply_text('Такого события - нет')
            return ConversationHandler.END
    return EDIT_EVENT


def edit_event(update, context):
    """После получения всей необходимой информации, используем функцию
    edit_user_events для редактирования события """
    event = context.chat_data['event']
    event_id = list(event.keys())[0]
    result = Calendar.edit_user_events(update.message.chat_id, event_id,
                                       context.chat_data['edit_object'], update.message.text)
    update.message.reply_text(f'{result}')
    return ConversationHandler.END


def delete_all_events(update, context):
    """Спрашивание об удалении всех заметок"""
    update.message.reply_text("""*Вы уверены?*
Да-'Y'/Нет-'N'
""", parse_mode='Markdown')
    return CHOOSE_TO_DELETE

def check_chose_to_delete(update, context):
    """В зависимости от сообщения - удаление файлов
    (С помощью итераци событий через delete_user_events)"""
    chose = update.message.text
    if chose.lower() == 'y':
        if Calendar.return_user_events(update.message.chat_id):  # проверка на наличие событий
            context.chat_data["all_events"] = Calendar.return_user_events(update.message.chat_id)
            for event in context.chat_data['all_events']:
                id_of_event = list(event.keys())[0]
                result = Calendar.delete_user_events(update.message.chat_id, id_of_event)
                update.message.reply_text(f"{result}")
            update.message.reply_text("*Все события удалены успешно!*", parse_mode='markdown')
            return ConversationHandler.END
        update.message.reply_text("Событий - нет")
        return ConversationHandler.END
    update.message.reply_text("Действие отменено!")
    return ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("create", ask_event_name),
        CommandHandler("read", choose_event),
        CommandHandler('delete', choose_event),
        CommandHandler('edit', choose_event),
        CommandHandler('display', display_events),
        CommandHandler('delete_all', delete_all_events),
    ],
    states={
        DETAILS: [MessageHandler(Filters.text & ~Filters.command, ask_event_details)],
        DATE: [MessageHandler(Filters.text & ~Filters.command, ask_event_date)],
        TIME: [MessageHandler(Filters.text & ~Filters.command, ask_event_time)],
        CREATE: [MessageHandler(Filters.text & ~Filters.command, create_event_handler)],
        CHECK_EXIST: [MessageHandler(Filters.text & ~Filters.command, check_exist_of_event)],
        ASK_FOR_CHANGE: [MessageHandler(Filters.text & ~Filters.command, ask_for_write_new_text)],
        EDIT_EVENT: [MessageHandler(Filters.text & ~Filters.command, edit_event)],
        CHOOSE_TO_DELETE: [MessageHandler(Filters.text & ~Filters.command, check_chose_to_delete)],

    },
    fallbacks=[CommandHandler("cancel", cancel)],
)


def main():
    """Создание обработчика conversation handler, запуск бота"""
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()


if __name__ == "__main__":
    main()
