"""Для хранения файлов - я использовал json."""
import json


class Calendar:
    """Этот класс - связка методов для хранения, чтения, изменения и удаления событий.
        Сами методы - не связаны с классом с точки зрения логики. Их можно достать из класса"""

    events = {}
    event_id = 1

    @classmethod
    def adding_event_to_file(cls, dict_event):
        """Этот метод - добавляет в файл 'events.jsonl' словарь-событие"""

        try:
            with open('events.jsonl', 'a', encoding='utf-8') as file:
                json.dump(dict_event, file)
                file.write('\n')
        except FileNotFoundError as err:
            print(f'Файл events.json - не существует {err}')

    @classmethod
    def create_and_add_event_to_file(cls, event_name, details, event_date, event_time, chat_id):
        """В этом методе - событие добавляется в словарь и в json файл,
        НО, в отличие от create_event, без повторной перезаписи файлов"""

        event = {
            'name': event_name,
            'details': details,
            'date': event_date,
            'time': event_time,
            'id': chat_id
        }

        cls.event_id += 1
        cls.events[cls.event_id] = event
        dict_event = {cls.event_id: event}
        cls.adding_event_to_file(dict_event)
        return cls.event_id

    @classmethod
    def check_missing_id(cls):
        """Этот метод - проверяет недостающие Id из списка. Добавляет их по порядку,
                            даже если какое-то событие удалили"""
        list_of_keys = list(cls.events.keys())
        int_list_of_keys = list(map(int, list_of_keys))
        expected_keys = list(range(1, max(int_list_of_keys) + 1))
        missing_keys = list(set(expected_keys) - set(int_list_of_keys))
        if missing_keys:
            return missing_keys[0]
        return len(cls.events) + 1

    @classmethod
    def update_all_events(cls):  # TODO переделать под формат json lines
        """Обновляет список событий из файла events.json, вытягивает их"""
        try:
            with open('events.json', 'r', encoding='utf-8') as file:
                cls.events = json.load(file)
        except FileNotFoundError as err:
            print(f'file events.json was not found {err}')

    @classmethod
    def write_all_events_to_file(cls):  # записывает события в файл events.json
        """Добавление события в словарь self.events. Номер события (id) - его ключ"""

        try:
            with open('events.json', 'w', encoding='utf-8') as file:
                json.dump(cls.events, file, indent=2)
        except FileNotFoundError as err:
            print(f'Файл events.json - не существует {err}')

    @classmethod
    def create_event(cls, event_data):
        """Создание события, сразу достает информацию из файла и записывает её обратно
         с помощью функций cls.update_events() и cls.write_events_to_file()"""
        cls.update_all_events()
        event_id = cls.check_missing_id()

        event = {
            'name': event_data['event_name'],
            'details': event_data['details'],
            'event_date': event_data['event_date'],
            'event_time': event_data['event_time'],
            'chat_id': event_data['chat_id']
        }
        cls.events[event_id] = event
        cls.write_all_events_to_file()
        return event_id

    @classmethod
    def return_user_events(cls, chat_id):
        """Возвращает список всех событий пользователя (включая id и сами события)
        События находятся за счет chat_id пользователя"""
        cls.update_all_events()
        user_events = []
        for event in cls.events:
            if cls.events[event]['chat_id'] == chat_id:
                user_events.append({event: cls.events[event]})
        return user_events

    @classmethod
    # TODO Переделать удаление не за счет перезаписи всего файла
    def delete_user_events(cls, chat_id, id_of_event):
        """Удаляет элемент словаря, проверка принадлежности события происходит
         за счет сравнения chat id"""
        cls.update_all_events()
        if cls.events[id_of_event]['chat_id'] == chat_id:
            del cls.events[id_of_event]
            cls.write_all_events_to_file()
            return f'Событие под номером {id_of_event} - удалено успешно!'
        return "Произошла ошибка. Возможно, такого события - не существует"

    @classmethod
    def edit_user_events(cls, chat_id, id_of_event, edit_object, new_edit_object):
        """Редактирование элемента события. Сначала обновляются все события,
        а потом с проверяем принадлежность и уже изменяем его,
        так же записываем изменения"""
        cls.update_all_events()
        if cls.events[id_of_event]['chat_id'] == chat_id:
            cls.events[id_of_event][edit_object] = new_edit_object
            cls.write_all_events_to_file()
            return f'Событие под номером {id_of_event} - изменено успешно!'
        return "Произошла ошибка. Возможно, такого события - не существует"
