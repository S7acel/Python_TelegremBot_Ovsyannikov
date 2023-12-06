import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from secrets import API_TOKEN
from Notes2 import build_note, read_note, edit_note

nt_nm = ''


def greeting(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='привет!)')


def message_handler(update, context):  # обработчик сообщений, применение словаря для функций
    # Создание заметки
    global nt_nm
    if context.user_data['command'] == 'create_note_handler':
        result = build_note(nt_nm, update.message.text, str(update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        nt_nm = ''
        context.user_data['command'] = None
    elif context.user_data['command'] == 'name_note_handler':
        nt_nm = str(update.message.text)  # Присваивание имени глобальной переменной nt_nm
        context.bot.send_message(chat_id=update.message.chat_id, text='Введите содержимое заметки')
        context.user_data[
            'command'] = 'create_note_handler'  # Перенаправление на создание заметки, при отправлении названия
    # чтение заметки
    elif context.user_data['command'] == 'read_note_handler':
        result = read_note(update.message.text, update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        context.user_data['command'] = None
    # Редактирование заметки
    elif context.user_data['command'] == 'edit_note_handler':
        context.user_data['note_name'] = update.message.text  # реализация запоминания заметки без глобальной функции
        context.bot.send_message(chat_id=update.message.chat_id, text='Напиши изменённый текст')
        context.user_data['command'] = 'final_edit_of_note'
    elif context.user_data['command'] == 'final_edit_of_note':
        result = edit_note(context.user_data['note_name'], str(update.message.chat_id), update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
def create_note_handler(update, context):  # спрашивание заметки, перенаправление на функцию создания словаря
    context.bot.send_message(update.message.chat_id, text='Введите название заметки')
    context.user_data['command'] = 'name_note_handler'


def edit_note_handler(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f'Введите название заметки')
    context.user_data['command'] = 'edit_note_handler'


def read_note_handler(update, context):
    context.bot.send_message(update.message.chat_id, text='Введите название заметки')
    context.user_data['command'] = 'read_note_handler'


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', greeting))
    dispatcher.add_handler(CommandHandler('read', read_note_handler))
    dispatcher.add_handler(CommandHandler('create', create_note_handler))
    dispatcher.add_handler(CommandHandler('edit', edit_note_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    updater.start_polling()


if __name__ == '__main__':
    main()
