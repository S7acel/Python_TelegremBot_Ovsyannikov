import os

def check_extension(f):  # Проверка на наличие '.txt' в конце
    try:
        if not f.endswith('.txt'):
            f += '.txt'
        return f
    except:
        print('Произошла ошибка')


def build_note(note_name, note_text):  # билд заметки (Для функции create note)
    try:
        note_name = check_extension(note_name)
        with open(note_name, 'w', encoding='utf-8') as f:
            f.write(note_text)
        print(f'Файл {note_name} создан успешно!\n')
    except:
        print("Произошла ошибка.")


def create_note():  # создание файла
    try:
        Name = input('Введите название файла\n')
        Text = input('Введите текст\n')
        build_note(Name, Text)
    except:
        print("Произошла ошибка.")


def read_note(name):  # Прочтение файла
    try:
        name = check_extension(name)
        if os.path.isfile(name):
            with open(name, 'r', encoding='utf-8') as f:
                text = f.read()
            print(text)
            return True
        else:
            print('Такого файла не существует.')
            return False
    except:
        print('Произошла ошибка')
        return False


def edit_note(name):  # редактирование заметки
    try:
        name = check_extension(name)
        if read_note(name):
            new_text = input('Введите новый текст: ')
            with open(name, 'w', encoding='utf-8') as f:
                f.write(new_text)
                print(f'Файл "{name}" Изменён успешно!')
        else:
            print('Что редактировать то? 😐')
    except:
        print('Произошла ошибка')


def delete_note(name):  # Удаление заметки
    try:
        name = check_extension(name)
        if os.path.isfile(name):
            os.remove(name)
            print(f'Заметка {name} удалена успешно')
        else:
            print('Нельзя удалить то, чего и так нет.')
    except:
        print('Произошла ошибка')


def display_notes():  # Вывод названий файлов в порядке увеличения длины
    try:
        notes = [note for note in os.listdir() if note.endswith('.txt')]
        reversed_notes = sorted(notes, key=len)
        if notes:
            for i in reversed_notes:
                print(i)
        else:
            print('Файлов пока что нет')
    except:
        print('Произошла ошибка')


def delete_all_notes():  # Удаление всех файлов
    try:
        notes = [note for note in os.listdir() if note.endswith('.txt')]
        if notes:
            for n in notes:
                delete_note(n)
            print('Все заметки удалены!')
        else:
            print('Файлов пока что нет')
    except:
        print('Произошла ошибка')
        return True


def main():  # объединение и вызовы функций
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
                return True
            case 2:
                note_name = input('Какую заметку вы хотите прочесть?\n')
                read_note(note_name)
                return True
            case 3:
                note_name = input('Какую заметку вы хотите изменить?\n')
                edit_note(note_name)
                return True
            case 4:
                note_name = input('Какую заметку вы хотите удалить?\n')
                delete_note(note_name)
                return True
            case 5:
                display_notes()
                return True
            case 6:
                output = input('Вы уверены? \n Да - "y" Нет - \"n\" ')
                if output == 'y':
                    delete_all_notes()
                    return True
                else:
                    return True
            case 7:
                ...
            case _:
                print('Ты должен выбрать в диапозоне от 1 до 7 ;)')
                return True
    except:
        print('Произошла ошибка!')
        return True


if __name__ == '__main__':
    while main():
        pass
