В этом коммите, я исправил проблему с логикой и работой обработчиков (от многоэтажной if-else в ней). Так же,
разложил все по директориям в ней и исправил пару ошибок в файле Notes2.
Изначально, я интересовался у эксперта, как исправить эту проблему:

```python
def message_handler(update, context):  # обработчик сообщений, применение словаря для функций для определения функции
    # Создание заметки
    global nt_nm
    if context.user_data['command'] == 'create_note_handler':
        result = build_note(context.user_data['note_name'], update.message.text, str(update.message.chat_id))
        context.bot.send_message(chat_id=update.message.chat_id, text=result)
        nt_nm = ''
        reset(context)
    elif context.user_data['command'] == 'name_note_handler':
        context.user_data['note_name'] = str(update.message.text)  # Присваивание имени глобальной переменной nt_nm
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
```

Проверки и перенаправление - очень мешали и нагружали код..
И эксперт предложил метод execute. Он вызывает функцию по имени в словаре:

```
def read():
 # Некоторые действия
def write(x):
 # Некоторые действия
def execute(function):  # задаем execute то, какой словарь будет принимать
 functions[function]()
functions = {'read': read,
 'write': write}
userInput = input('Введите название функции:')
execute(userInput)
```

Но в моем случае, я нашел более улучшенный способ решения, направленный конкретно на мою задачу. Это класс **ConversationHandler**. В нем есть вступительные позиций (```entry points```) для вызова
диалога, промежуточные состояния
ния (states) для вызова других методов после выполнения функций и (fallbacks) - запасные варианты например:

```
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', greeting), CommandHandler('create', ask_note_name),
                  CommandHandler('random_number',
                                 ask_first_number)],
    states={
        FIRST: [MessageHandler(Filters.text & ~Filters.command, send_message)],
        SECOND: [MessageHandler(Filters.text & ~Filters.command, ask_note_content)],
        THIRD: [MessageHandler(Filters.text & ~Filters.command, create_note)],
        FOURTH: [MessageHandler(Filters.text & ~Filters.command, ask_second_note)],
        FIFTH: [MessageHandler(Filters.text & ~Filters.command, create_random_number)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)
```

И в нем, я придерживался этого класса.
Отредактированные функции:

- [x] Удаление всех заметок
- [x] Создание заметки
- [x] Прочтение заметки
- [X] Редактирование заметки
- [X] Удаление заметки

⬆️⬆️⬆️ Теперь каждая функция - раздроблена на более мелкие. Удобно и легко управляемо!
---