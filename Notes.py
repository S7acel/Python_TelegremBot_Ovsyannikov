import os


def build_note(note_name, note_text):
    if not note_name.endswith('.txt'):
        note_name += '.txt'
    with open(note_name, 'w', encoding='utf-8') as f:
        f.write(note_text)
    print(f'Файл {note_name} создан успешно!\n')


def create_note():
    Name = input('Введите название файла\n')
    Text = input('Введите текст\n')
    build_note(Name, Text)


def read_note(name):
    if not name.endswith('.txt'):
        name += '.txt'
    if os.path.isfile(name):
        with open(name, 'r', encoding='utf-8') as f:
            text = f.read()
        print(text)
        return True
    else:
        print('Такого файла не существует.')
        return False


def edit_note(name):
    if not name.endswith('.txt'):
        name += '.txt'
    if read_note(name):
        new_text = input('Введите новый текст: ')
        with open(name, 'w', encoding='utf-8') as f:
            f.write(new_text)
            print(f'{name} Изменена успешно!')
    else:
        print('Что редактировать то? 😐')


def delete_note(name):
    if not name.endswith('.txt'):
        name += '.txt'
    if os.path.isfile(name):
        os.remove(name)
        print(f'Заметка {name} удалена успешно')
    else:
        print('Нельзя удалить то, чего и так нет.')


def main():
    print('Здравствуйте, выберете действие, написав цифру:')
    print('''1 - создать заметку
2 - прочесть заметку
3 - изменить заметку
4 - удалить заметку''')
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


while True:
    main()
