import os

path = f'C:/Users/user/PycharmProjects/Python_TelegremBot_Ovsyannikov/Notes/'  # директория файла пользователей


def check_extension(f):  # Проверка на наличия '.txt' в конце
    try:
        if not f.endswith('.txt'):
            f += '.txt'
        return f
    except:
        print('Произошла ошибка')


def check_directory(pth):  # проверка существования файла для хранения заметки
    try:
        if not os.path.exists((pth)):
            os.mkdir(pth)
    except Exception as err:
        return f'Произошла ошибка {err}'


def build_note(note_name, note_text, chat_id):  # создание заметки
    try:
        check_directory(f'{path}/{chat_id}')
        note_name = check_extension(note_name)
        with open(f'{path}/{chat_id}/{note_name}', 'w', encoding='utf-8') as f:
            f.write(note_text)
        return f'Файл {note_name} создан успешно!\n'
    except Exception as e:
        return f"Произошла ошибка. {e}"


def read_note(note_name, chat_id):  # Прочтение файла
    try:
        note_name = check_extension(note_name)
        if os.path.isfile(f'{path}/{chat_id}/{note_name}'):
            with open(f'{path}/{chat_id}/{note_name}', 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        else:
            return 'Такого файла не существует.'
    except Exception as err:
        return f'Произошла ошибка {f}'


def edit_note(name, chat_id, new_text):  # редактирование заметки
    try:
        name = check_extension(name)
        if os.path.exists(f'{path}/{chat_id}/{name}'):
            with open(f'{path}/{chat_id}/{name}', 'w', encoding='utf-8') as f:
                f.write(str(new_text))
                return (f'Файл "{name}" Изменён успешно!')
        else:
            return ('Я не знаю такого файла, может ошибся? 😐')
    except Exception as err:
        return f'Произошла ошибка {err}'


def delete_note(name, chat_id):  # Удаление заметки
    try:
        name = check_extension(name)
        if os.path.isfile(f'{path}/{chat_id}/{name}'):
            os.remove(f'{path}/{chat_id}/{name}')
            return (f'Заметка {name} удалена успешно')
        else:
            return ('Нельзя удалить то, чего и так нет.')
    except Exception as err:
        return (f'Произошла ошибка {err}')


def display_notes(chat_id):  # Вывод названий файлов в порядке увеличения длины
    try:
        notes = os.listdir(f'{path}/{chat_id}')
        reversed_notes = sorted(notes, key=len)
        return reversed_notes
    except Exception as err:
        print(f'Произошла ошибка {err}')


def delete_all_notes(chat_id):  # Создание списка всех файлов
    try:
        notes = os.listdir(f'{path}/{chat_id}')
        reversed_notes = sorted(notes, key=len)
        if reversed_notes:
            for i in reversed_notes:
                delete_note(i, chat_id)
            return f'Все заметки удалены успешно! ({", ".join(reversed_notes)})'
        else:
            return f'Заметок пока что нет'
    except Exception as err:
        return f'Произошла ошибка {err}'
