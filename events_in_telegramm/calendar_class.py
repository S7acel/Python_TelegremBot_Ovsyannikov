"""Для хранения файлов - я использовал json."""
import json
import psycopg2
from config import HOST, USER, PASSWORD, DB_NAME, PORT


class InstanceCreationNotAllowedError(Exception):
    """Raised when an instance creation is not allowed"""


class Calendar:
    """Этот класс - связка методов для хранения, чтения, изменения и удаления событий.
        Сами методы - не связаны с классом с точки зрения логики. Их можно достать из класса"""
    connection = None
    events = {}

    def __new__(cls, *args, **kwargs):
        """Исключение для того чтобы не создавать экземпляры класса"""
        raise InstanceCreationNotAllowedError("Нельзя создать экземпляр этого класса")

    @classmethod
    def write_user_in_table(cls, chat_id, first_name, username):
        """Этот метод записывает информацию о пользователе в таблицу users"""
        query_for_check = """SELECT EXISTS(SELECT 1 FROM users WHERE id = %s)"""
        id_data = (chat_id,)
        query = """INSERT INTO users (id, first_name, username) VALUES (%s, %s, %s)"""
        data = (chat_id, first_name, username)
        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                cursor.execute(query_for_check, id_data)
                result = cursor.fetchone()[0]
                print(f"[INFO] user's id was successfully checked \n Result: {result}")
                if not result:
                    cursor.execute(query, data)
                    print('[INFO] Data was successfully inserted')
                    return 'Информация была успешно добавлена в базу данных!'
                return 'Информация уже есть в таблице!'
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Произошла ошибка при работе с PostgreSQL: ' + str(_err)
        finally:
            Calendar.close_connection_with_database()

    @classmethod
    def create_connection_with_database(cls):
        try:
            cls.connection = psycopg2.connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DB_NAME,
                port=PORT
            )
            cls.connection.autocommit = True
            print(f'[INFO] connection was created! ({cls.connection.closed})')
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)

    @classmethod
    def close_connection_with_database(cls):
        try:
            if cls.connection:
                cls.connection.close()
                print(f'[INFO] PostgreSQL connection closed ({cls.connection.closed})')

        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)

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
    def check_existance_of_user(cls):
        ...

    @classmethod
    def add_event_to_database(cls, event_name, details, event_date, event_time, chat_id):
        """В этом методе - событие добавляется в словарь и в json файл,
        НО, в отличие от create_event, без повторной перезаписи файлов.
        Соединение изначально происходит в функции check_missing_id"""
        event_id = Calendar.check_missing_id()
        query_for_event_table = """INSERT INTO events (event_id, event_name, event_details, event_date, event_time)
        VALUES (%s, %s, %s, %s, %s)"""
        data_for_event_table = (event_id, event_name, details, event_date, event_time)
        query_for_user_event = """INSERT INTO user_event (event_id, user_id)
        VALUES (%s, %s)"""
        data_for_user_event = (event_id, chat_id)

        try:
            with cls.connection.cursor() as cursor:
                """Добавление в таблицу events"""
                cursor.execute(query_for_event_table, data_for_event_table)
                print('[INFO] Event was successfully inserted')


                """Добавление в таблицу user_event"""
                cursor.execute(query_for_user_event, data_for_user_event)
                print('[INFO] User_event was successfully inserted')
                return f"Событие '{event_name}' успешно создано и имеет id {event_id}"
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return f'Введены неправильные значения!'
        finally:
            Calendar.close_connection_with_database()

    @classmethod
    def check_missing_id(cls):
        """Этот метод - проверяет недостающие Id из базы. Добавляет их по порядку,
                            даже если какое-то событие удалили"""

        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                cursor.execute("""SELECT event_id from events""")
                print('[INFO] ids was successfully received')
                id_of_events = [id[0] for id in cursor.fetchall()]
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Произошла ошибка при работе с PostgreSQL: ' + str(_err)

        if id_of_events:
            expected_keys = list(range(1, max(id_of_events) + 1))
            missing_keys = list(set(expected_keys) - set(id_of_events))
            if missing_keys:
                return missing_keys[0]
            return len(id_of_events) + 1
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
        query = """
        select 
            e.event_id, 
            e.event_name, 
            e.event_details,
            e.event_date, 
            e.event_time
        from user_event us
        inner join events e 
        on e.event_id = us.event_id 
        where user_id = %s
        """
        data = (chat_id,)
        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                cursor.execute(query, data)
                result = cursor.fetchall()
                print('[INFO] events was successfully received')
                for el in result:
                    event_data = {"name": el[1], "details": el[2], "date": el[3], "time": el[4], "id": chat_id}
                    user_events.append({el[0]: event_data})
                return user_events
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Произошла ошибка при работе с PostgreSQL: ' + str(_err)
        finally:
            Calendar.close_connection_with_database()

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
