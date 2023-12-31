from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler
from do_not_save_files.secrets import API_TOKEN
from notes2 import build_note, read_note, edit_note, delete_note, display_notes, delete_all_notes, logging

DELETE_ALL, DETAILS, CREATE, READ, EDIT_DETAILS, EDIT, DELETE = range(7)


def greeting(update, context):  # функция-обработчик (Запускается по команде /start)
    text = 'Привет, я NoteWizard - твой личный помощник для создания заметок. Я могу помочь тебе создавать заметки и ' \
           'сохранять их в отдельных папках. Мои команды включают в себя:\n\n/create - ' \
           'создать новую заметку.\n/read - прочитать существующую заметку.\n/edit - изменить существующую ' \
           'заметку.\n/delete - удалить существующую заметку.\n/display - отобразить список всех ' \
           'заметок.\n/delete_all_notes - удалить все заметки.\n\nЧтобы узнать больше о моих возможностях, ' \
           'используйте команду /help. Давай начнем работу!'
    context.bot.send_message(chat_id=update.message.chat_id, text=text)
    logging(update.message.chat_id)


def help_handler(update, context):  # функция-обработчик (Запускается по команде /help)
    context.bot.send_message(chat_id=update.message.chat_id, text='Ух-ты! На этом весь мой функционал закончился! :( '
                                                                  '\n Если есть предложения, или рекомендации по '
                                                                  'улучшению бота, то напишите сюда --> @Markceil\n '
                                                                  'Был бы очень благодарен 🤩')


def display_notes_handler(update, context):  # функция обработчик отправление названий всех файлов
    notes_list = display_notes(update.message.chat_id)
    if notes_list:
        for i in notes_list:
            context.bot.send_message(chat_id=update.message.chat_id, text=str(i))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text='Файлов пока что нет')


def ask_to_delete_all_notes_handler(update, context):  # Спрашивание об удалении файлов
    # Изначальная проверка наличия файлов
    if display_notes(update.message.chat_id):
        update.message.reply_text(
            f'Вы уверены? Удаляемые файлы: {", ".join(display_notes(update.message.chat_id))} \n Да - y/ Нет - n')
        return DELETE_ALL
    else:
        update.message.reply_text(f'Заметок - нет 👿')
        return ConversationHandler.END


def delete_all_handler(update, context):
    result = delete_all_notes(update.message.chat_id, update.message.text)
    update.message.reply_text(f'{result}')
    return conversation_handler.END


def ask_note_name_handler(update, context):
    update.message.reply_text(f'Напиши название для новой заметки')
    return DETAILS


def details_note_handler(update, context):
    context.user_data['note_name'] = update.message.text
    update.message.reply_text(f"Напиши содержимое заметки {context.user_data['note_name']}")
    return CREATE


def create_note_handler(update, context):
    result = build_note(context.user_data['note_name'], update.message.text, str(update.message.chat_id))
    update.message.reply_text(f'{result}')
    return ConversationHandler.END


def read_name_handler(update, context):
    update.message.reply_text(f"Напиши название заметки")
    return READ


def read_note_handler(update, context):
    result = read_note(update.message.text, update.message.chat_id)
    update.message.reply_text(f"{result}")
    return ConversationHandler.END


def ask_name_of_edit_handler(update, context):
    update.message.reply_text(f"Напиши название заметки")
    return EDIT_DETAILS


def ask_details_of_edit_handler(update, context):
    context.user_data['note_name'] = update.message.text
    update.message.reply_text(f"Напиши содержимое заметки {update.message.text}")
    return EDIT


def final_edit_handler(update, context):
    result = edit_note(context.user_data['note_name'], str(update.message.chat_id), update.message.text)
    update.message.reply_text(f"{result}")
    return ConversationHandler.END


def ask_delete_note(update, context):
    update.message.reply_text(f'Напиши название заметки')
    return DELETE

def delete_handler(update, context):
    result = delete_note(update.message.text, update.message.chat_id)
    update.message.reply_text(f"{result}")
    return ConversationHandler.END

conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', greeting),
                  CommandHandler('delete_all_notes', ask_to_delete_all_notes_handler),
                  CommandHandler('create', ask_note_name_handler), CommandHandler('read', read_name_handler),
                  CommandHandler('edit', ask_name_of_edit_handler), CommandHandler('delete', ask_delete_note)],
    states={
        DELETE_ALL: [MessageHandler(Filters.text & ~Filters.command, delete_all_handler)],
        DETAILS: [MessageHandler(Filters.text & ~Filters.command, details_note_handler)],
        CREATE: [MessageHandler(Filters.text & ~Filters.command, create_note_handler)],
        READ: [MessageHandler(Filters.text & ~Filters.command, read_note_handler)],
        EDIT_DETAILS: [MessageHandler(Filters.text & ~Filters.command, ask_details_of_edit_handler)],
        EDIT: [MessageHandler(Filters.text & ~Filters.command, final_edit_handler)],
        DELETE: [MessageHandler(Filters.text & ~Filters.command, delete_handler)]
    },
    fallbacks=[CommandHandler('cancel', greeting)]
)


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', greeting))
    dispatcher.add_handler(CommandHandler('display', display_notes_handler))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(conversation_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()
