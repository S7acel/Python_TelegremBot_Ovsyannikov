'''Модуль os необходим для того чтобы работать с файлами операционной системы'''
import os


def check_extension(f):
    '''Проверка на наличие '.txt' в конце. Добавляет к названию файла .txt,
     в случае его отсутствия'''
    try:
        if not f.endswith('.txt'):
            f += '.txt'
        return f
    except AttributeError as err:
        print(f'Произошла ошибка {err}')
        return None


def build_note(note_name, note_text):
    ''' создание заметки реализация происходит за счет менеджера контекста with open'''
    try:
        note_name = check_extension(note_name)
        with open(note_name, 'w', encoding='utf-8') as f:
            f.write(note_text)
        print(f'Файл {note_name} создан успешно!\n')
    except IOError as err:
        print(f"Произошла ошибка. {err}")


def create_note():
    '''создание файла происходит за счет вызова функции build_note()
    и спрашивания имени и текста заметки'''
    try:
        name = input('Введите название файла\n')
        text = input('Введите текст\n')
        build_note(name, text)
    except (IOError, KeyboardInterrupt):
        print("Произошла ошибка.")


def read_note(name):
    '''Реализуется за счет менеджера контекста. Происходит проверка наличия файла в системе
     и вывод текста, в случае его наличия'''
    try:
        name = check_extension(name)
        if os.path.isfile(name):
            with open(name, 'r', encoding='utf-8') as f:
                text = f.read()
            print(text)
            return True
        print('Такого файла не существует.')
        return False
    except IOError as err:
        print(f'Произошла ошибка {err}')
        return False


def edit_note(name):  # редактирование заметки
    '''Происходит проверка посредством вызова функции read note.
    Сначала выводит содержимое файла (в случае успеха)
    и далее требует новый текст для изменения'''
    try:
        name = check_extension(name)
        if read_note(name):
            new_text = input('Введите новый текст: ')
            with open(name, 'w', encoding='utf-8') as f:
                f.write(new_text)
                print(f'Файл "{name}" Изменён успешно!')
        else:
            print('Что редактировать то? 😐')
    except IOError as err:
        print(f'Произошла ошибка {err}')


def delete_note(name):
    '''Удаление заметки за счет функции os.remove'''
    try:
        name = check_extension(name)
        if os.path.isfile(name):
            os.remove(name)
            print(f'Заметка {name} удалена успешно')
        else:
            print('Нельзя удалить то, чего и так нет.')
    except IOError as err:
        print(f'Произошла ошибка {err}')


def display_notes():
    '''Вывод названий файлов в порядке увеличения длины'''
    try:
        # создание списка .txt файлов, найденных в директории
        notes = [note for note in os.listdir()
                 if note.endswith('.txt')]
        reversed_notes = sorted(notes, key=len)
        if notes:
            for i in reversed_notes:
                print(i)
        else:
            print('Файлов пока что нет')
    except IOError as err:
        print(f'Произошла ошибка {err}')


def delete_all_notes():
    '''Удаление всех заметок'''
    try:
        # создание списка .txt файлов, найденных в директории
        notes = [note for note in os.listdir()
                 if note.endswith('.txt')]
        if notes:
            for n in notes:
                delete_note(n)
            print('Все заметки удалены!')
        else:
            print('Файлов пока что нет')
    except IOError as err:
        print(f'Произошла ошибка {err}')


def main():
    ''' объединение и вызовы функций'''
    result = True
    try:
        print('Выберете действие, написав цифру:', end='')
        print('''
    1 - создать заметку
    2 - Прочесть заметку
    3 - Изменить заметку
    4 - Удалить заметку
    5 - Посмотреть созданные файлы
    6 - Удалить все файлы
    7 - Выход''')
        func = int(input('Ввод: '))
        match func:
            case 1:
                create_note()
            case 2:
                note_name = input('Какую заметку вы хотите прочесть?\n')
                read_note(note_name)
            case 3:
                note_name = input('Какую заметку вы хотите изменить?\n')
                edit_note(note_name)
            case 4:
                note_name = input('Какую заметку вы хотите удалить?\n')
                delete_note(note_name)
            case 5:
                display_notes()
            case 6:
                output = input('Вы уверены? \n Да - "y" Нет - \"n\" ')
                if output == 'y':
                    delete_all_notes()
            case 7:
                ...
            case _:
                print('Ты должен выбрать в диапозоне от 1 до 7 ;)')
    except (ValueError, KeyboardInterrupt) as err:
        print(f'Произошла ошибка! {err}')
        result = True
    return result



if __name__ == '__main__':
    while main():
        pass
