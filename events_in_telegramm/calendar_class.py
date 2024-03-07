"""Для хранения файлов - я использовал json."""
import json


class InstanceCreationNotAllowedError(Exception):
    """Raised when an instance creation is not allowed"""


class Calendar:
    """Этот класс - связка методов для хранения, чтения, изменения и удаления событий.
        Сами методы - не связаны с классом с точки зрения логики. Их можно достать из класса"""

    events = {}

    def __new__(cls, *args, **kwargs):
        """Исключение для того чтобы не создавать экземпляры класса"""
        raise InstanceCreationNotAllowedError("Нельзя создать экземпляр этого класса")

    @classmethod
    def check_exist_of_event(cls, event, chat_id):
        """В этой функции проверяется существование данного события.
            В случае неправильного написания, словарь не найдется в списке
            и отправится сообщение о его не существовании."""
        user_event = {}
        try:
            event_id = int(event.split()[-1].strip('()'))  # получение id из сообщения пользователя
        except ValueError:
            return None
        for dict_event in cls.return_user_events(chat_id):  # итерация всех событий владельца
            if list(dict_event.keys())[0] == event_id:
                user_event = dict_event  # добавление выбранного события в словарь
                break
        return user_event

    @classmethod
    def adding_event_to_file(cls, dict_event, mode='a'):
        """Этот метод - добавляет в файл 'events.jsonl' словарь-событие"""

        try:
            with open('events.jsonl', mode, encoding='utf-8') as file:
                for event_id, event_data in dict_event.items():
                    event = {event_id: event_data}
                    json.dump(event, file)
                    file.write('\n')
        except FileNotFoundError as err:
            print(f'Файл "events.jsonl"- не существует {err}')

    @classmethod
    def create_and_add_event_to_file(cls, event_name, details, event_date, event_time, chat_id):
        """В этом методе - событие добавляется в словарь и в json файл,
        НО, в отличие от create_event, без повторной перезаписи файлов"""
        event_id = Calendar.check_missing_id()

        event = {
            'name': event_name,
            'details': details,
            'date': event_date,
            'time': event_time,
            'id': chat_id
        }

        cls.events[event_id] = event
        dict_event = {event_id: event}
        cls.adding_event_to_file(dict_event)
        return event_id

    @classmethod
    def check_missing_id(cls):
        """Этот метод - проверяет недостающие Id из списка. Добавляет их по порядку,
                            даже если какое-то событие удалили"""
        if cls.events:
            list_of_keys = list(cls.events.keys())
            expected_keys = list(range(1, max(list_of_keys) + 1))
            missing_keys = list(set(expected_keys) - set(list_of_keys))
            if missing_keys:
                return missing_keys[0]
            return len(cls.events) + 1
        return 1

    @classmethod
    def update_all_events(cls):
        """Обновляет список событий из файла events.jsonl, вытягивает их.
        Построчно итерирует события из класса и добавляет в словарь events"""
        try:
            with open('events.jsonl', 'r', encoding='utf-8') as file:
                for iter_event in file:
                    whole_event = json.loads(iter_event)
                    event_values = list(whole_event.values())[0]
                    event_id = int(list(whole_event.keys())[0])
                    cls.events[event_id] = event_values
        except FileNotFoundError as err:
            print(f'file was not found {err}')

    @classmethod
    def return_user_events(cls, chat_id):
        """Возвращает список всех событий пользователя (включая id и сами события)
        События находятся за счет chat_id пользователя"""
        user_events = []
        for event_id, event_data in cls.events.items():
            if event_data["id"] == chat_id:
                user_events.append({event_id: event_data})
        return user_events

    @classmethod
    def delete_user_events(cls, chat_id, id_of_event):
        """Удаляет элемент словаря, проверка принадлежности события происходит
         за счет сравнения chat id"""
        if cls.events[id_of_event]['id'] == chat_id:
            del cls.events[id_of_event]
            cls.adding_event_to_file(cls.events, mode='w')
            return f'Событие под номером {id_of_event} - удалено успешно!'
        return "Произошла ошибка. Возможно, такого события - не существует"

    @classmethod
    def edit_user_events(cls, chat_id, id_of_event, edit_object, new_edit_object):
        """Редактирование элемента события. Проверка принадлежности к событию
        и перезапись всех файлов"""
        if cls.events[id_of_event]['id'] == chat_id:
            cls.events[id_of_event][edit_object] = new_edit_object
            cls.adding_event_to_file(cls.events, mode='w')
            return f'Событие под номером {id_of_event} - изменено успешно!'
        return "Произошла ошибка. Возможно, такого события - не существует"


Calendar.update_all_events()
