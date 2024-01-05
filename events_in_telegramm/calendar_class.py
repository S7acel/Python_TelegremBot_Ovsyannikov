import os
import datetime
import json
from datetime import datetime

"""
Для хранения файлов - я использовал json.
"""


class Calendar:
    events = {}

    # проверка недостающих ключей (если события с id - были удалены)
    @classmethod
    def check_missing_id(cls):
        list_of_keys = list(cls.events.keys())
        int_list_of_keys = list(map(int, list_of_keys))
        expected_keys = list(range(1, max(int_list_of_keys) + 1))
        missing_keys = list(set(expected_keys) - set(int_list_of_keys))
        if missing_keys:
            return missing_keys[0]
        else:
            return len(cls.events) + 1

    # обновляет список событий из файла events.json, вытягивает их
    @classmethod
    def update_events(cls):
        with open('events.json', 'r') as file:
            cls.events = json.load(file)

    # Добавление события в словарь self.events. Номер события (id) - его ключ
    @classmethod
    def write_events_to_file(cls):  # записывает события в файл events.json
        with open('events.json', 'w', encoding='utf-8') as file:
            json.dump(cls.events, file, indent=2)

    # Создание события, достает информацию из файла и записывает её обратно с помощью функций Calendar.update_events()
    # и Calendar.write_events_to_file()
    @classmethod
    def create_event(cls, event_name, event_details, event_date, event_time, chat_id):
        Calendar.update_events()
        event_id = Calendar.check_missing_id()

        event = {
            'name': event_name,
            'details': event_details,
            'event_date': event_date,
            'event_time': event_time,
            'chat_id': chat_id
        }
        cls.events[event_id] = event
        Calendar.write_events_to_file()
        return event_id

    # Возвращает список владельца событий
    @classmethod
    def return_user_events(cls, chat_id):
        Calendar.update_events()
        user_events = []
        for i in cls.events:
            if cls.events[i]['chat_id'] == chat_id:
                user_events.append({i: cls.events[i]})
        return user_events

    # удаляет элемент словаря по id
    @classmethod
    def delete_user_events(cls, chat_id, id_of_event):
        Calendar.update_events()
        if cls.events[id_of_event]['chat_id'] == chat_id:
            del cls.events[id_of_event]
            Calendar.write_events_to_file()
            return f'Событие под номером {id_of_event} - удалено успешно!'
        return f"Произошла ошибка. Возможно, такого события - не существует"

    # редактирование элемента события
    @classmethod
    def edit_user_events(cls, chat_id, id_of_event, edit_object, new_edit_object):
        Calendar.update_events()
        if cls.events[id_of_event]['chat_id'] == chat_id:
            cls.events[id_of_event][edit_object] = new_edit_object
            Calendar.write_events_to_file()
            return f'Событие под номером {id_of_event} - изменено успешно!'
        return f"Произошла ошибка. Возможно, такого события - не существует"
