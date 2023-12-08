import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from secrets import API_TOKEN
from Notes2 import build_note, read_note, edit_note, delete_note, display_notes, delete_all_notes

nt_nm = ''


def reset(context):  # удаление информации после выполнения функции
    context.user_data['command'] = None
    context.user_data['note_name'] = None


def greeting(update, context):
    text = 'Привет, я NoteWizard - твой личный помощник для создания заметок. Я могу помочь тебе создавать заметки и ' \
           'сохранять их в отдельных папках. Мои команды включают в себя:\n\n/create - ' \
           'создать новую заметку.\n/read - прочитать существующую заметку.\n/edit - изменить существующую ' \
           'заметку.\n/delete - удалить существующую заметку.\n/display - отобразить список всех ' \
           'заметок.\n/delete_all_notes - удалить все заметки.\n\nЧтобы узнать больше о моих возможностях, ' \
           'используйте команду /help. Давай начнем работу!'
    context.bot.send_message(chat_id=update.message.chat_id, text=text)

def help_handler(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Ух-ты! На этом весь мой функционал закончился! :( '
                                                                  '\n Если есть предложения, или рекомендации по '
                                                                  'улучшению бота, то напишите сюда --> @Markceil\n '
                                                                  'Был бы очень благодарен 🤩')

def delete_all_notes_handler(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Вы уверены? \n Да - "Y" Нет - \"N\" ')
    context.user_data['command'] = 'delete_all_notes_handler'


def create_note_handler(update, context):  # спрашивание заметки, перенаправление на функцию создания словаря
    context.bot.send_message(update.message.chat_id, text='Введите название заметки')
    context.user_data['command'] = 'name_note_handler'


def display_notes_handler(update, context):
    notes_list = display_notes(update.message.chat_id)
    if notes_list:
        for i in notes_list:
            context.bot.send_message(chat_id=update.message.chat_id, text=str(i))
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text='Файлов пока что нет')


def read_note_handler(update, context):  # функция-обработчик спрашивание название файла
    context.bot.send_message(update.message.chat_id, text='Введите название заметки')
    context.user_data['command'] = 'read_note_handler'


def edit_note_handler(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=f'Введите название заметки')
    context.user_data['command'] = 'edit_note_handler'


def delete_note_handler(update, context):  # функция обработчик удаление заметки
    context.bot.send_message(chat_id=update.message.chat_id, text='Какую заметку вы хотите удалить?')
    context.user_data['command'] = 'delete_note'


def message_handler(update, context):  # обработчик сообщений, применение словаря для функций для определения функции
    # Создание заметки
    global nt_nm
    if context.user_data['command'] == 'create_note_handler':
        result = build_note(nt_nm, update.message.text, str(update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        nt_nm = ''
        reset(context)
    elif context.user_data['command'] == 'name_note_handler':
        nt_nm = str(update.message.text)  # Присваивание имени глобальной переменной nt_nm
        context.bot.send_message(chat_id=update.message.chat_id, text='Введите содержимое заметки')
        context.user_data[
            'command'] = 'create_note_handler'  # Перенаправление на создание заметки, при отправлении названия
    # чтение заметки
    elif context.user_data['command'] == 'read_note_handler':
        result = read_note(update.message.text, update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        reset(context)
    # Редактирование заметки
    elif context.user_data['command'] == 'edit_note_handler':
        context.user_data['note_name'] = update.message.text  # реализация запоминания заметки без глобальной функции
        context.bot.send_message(chat_id=update.message.chat_id, text='Напиши изменённый текст')
        context.user_data['command'] = 'final_edit_of_note'
    elif context.user_data['command'] == 'final_edit_of_note':
        result = edit_note(context.user_data['note_name'], str(update.message.chat_id), update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        reset(context)
    elif context.user_data['command'] == 'delete_all_notes_handler':
        if update.message.text == 'Y':
            result = delete_all_notes(update.message.chat_id)
            context.bot.send_message(chat_id=update.message.chat_id, text=result)
            reset(context)
        else:
            context.bot.send_message(chat_id=update.message.chat_id, text='Действие отменено!')
            reset(context)
    # Удаление заметки
    elif context.user_data['command'] == 'delete_note':
        result = delete_note(update.message.text, update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        reset(context)
    # Удаление заметки


def main():
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', greeting))
    dispatcher.add_handler(CommandHandler('read', read_note_handler))
    dispatcher.add_handler(CommandHandler('create', create_note_handler))
    dispatcher.add_handler(CommandHandler('edit', edit_note_handler))
    dispatcher.add_handler(CommandHandler('delete', delete_note_handler))
    dispatcher.add_handler(CommandHandler('display', display_notes_handler))
    dispatcher.add_handler(CommandHandler('delete_all_notes', delete_all_notes_handler))
    dispatcher.add_handler(CommandHandler('help', help_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    updater.start_polling()


if __name__ == '__main__':
    main()
