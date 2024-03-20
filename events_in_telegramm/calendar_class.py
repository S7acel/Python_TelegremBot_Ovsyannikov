"""Для хранения файлов - я использовал json."""
import psycopg2
from config import HOST, USER, PASSWORD, DB_NAME, PORT


class InstanceCreationNotAllowedError(Exception):
    """Raised when an instance creation is not allowed"""


class Calendar:
    """Этот класс - связка методов для хранения, чтения, изменения и удаления событий.
        Сами методы - не связаны с классом с точки зрения логики. Их можно достать из класса"""
    connection = None

    def __new__(cls, *args, **kwargs):
        """Исключение для того чтобы не создавать экземпляры класса"""
        raise InstanceCreationNotAllowedError("Нельзя создать экземпляр этого класса")

    @classmethod
    def write_user_in_table(cls, chat_id, first_name, username):
        """Этот метод записывает информацию о пользователе в таблицу users, делает проверку"""
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
            print('[INFO] Error while working with PostgreSQL', _err)
            return 'Произошла ошибка при работе с PostgreSQL: ' + str(_err)
        finally:
            Calendar.close_connection_with_database()

    @classmethod
    def create_connection_with_database(cls):
        """Этот метод создает соединение с базой данных. Далее, при вызове курсора,
        с базой можно взаимодействовать"""
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
        """Этот метод закрывает соединение с базой данных.
        После действий в базе данных, он закрывается"""
        try:
            if cls.connection:
                cls.connection.close()
                print(f'[INFO] PostgreSQL connection closed ({cls.connection.closed})')

        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)

    @classmethod
    def check_belong_event_to_user(cls, event, chat_id): # TODO додедать проверку
        """В этой функции проверяется принадлежность события к пользователю.
            В случае неправильного написания, словарь не найдется в списке
            и отправится сообщение о его не существовании."""
        return True

    @classmethod
    def add_event_to_database(cls, event_name, details, event_date, event_time, chat_id):
        """В этом методе - событие добавляется в словарь и в json файл,
        НО, в отличие от create_event, без повторной перезаписи файлов.
        Соединение изначально происходит в функции check_missing_id"""
        event_id = Calendar.check_missing_id()
        query_for_event_table = """INSERT INTO
        events (event_id, event_name, event_details, event_date, event_time)
        VALUES (%s, %s, %s, %s, %s)"""
        data_for_event_table = (event_id, event_name, details, event_date, event_time)
        query_for_user_event = """INSERT INTO user_event (event_id, user_id)
        VALUES (%s, %s)"""
        data_for_user_event = (event_id, chat_id)

        try:
            with cls.connection.cursor() as cursor:
                # Добавление в таблицу events
                cursor.execute(query_for_event_table, data_for_event_table)
                print('[INFO] Event was successfully inserted')
                # Добавление в таблицу user_event
                cursor.execute(query_for_user_event, data_for_user_event)
                print('[INFO] User_event was successfully inserted')
                return f"Событие '{event_name}' успешно создано и имеет id {event_id}"
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Введены неправильные значения!'
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
    def return_user_events(cls, chat_id, event_id=None):
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
        if event_id is not None:
            query += " and e.event_id = %s"
            data = (chat_id, event_id)
        else:
            data = (chat_id,)
        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                cursor.execute(query, data)
                result = cursor.fetchall()
                print('[INFO] events was successfully received!')
                return result
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Произошла ошибка при работе с PostgreSQL: ' + str(_err)
        finally:
            Calendar.close_connection_with_database()

    @classmethod
    def delete_user_events(cls, chat_id, id_of_event):
        """Удаляет из базы данных коннектор и событие. Изначально запросы
        с внешними ключами, а потом уже само событие.
        Сначала происходит удаление связи и пользователя из таблицы user_events
        """

        query_for_user_event = """
        delete from user_event 
        where user_id = %s and event_id = %s
        """
        data_for_user_event = (chat_id, id_of_event)
        query_for_event_table = """
        delete from events e
        where e.event_id = %s
        """
        data_for_event_table = (id_of_event,)

        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                # Удаление связи и пользователя из таблицы user_events
                cursor.execute(query_for_user_event, data_for_user_event)
                print('[INFO] User_Event was successfully deleted!')
                # Добавление в таблицу user_event
                cursor.execute(query_for_event_table, data_for_event_table)
                print('[INFO] event was successfully deleted!')
                return f"Событие под номером'{id_of_event}' успешно Удалено!"
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', _err)
            return 'Введены неправильные значения!'
        finally:
            Calendar.close_connection_with_database()

    @classmethod
    def edit_user_events(cls, chat_id, id_of_event, edit_object, new_edit_object):
        """Редактирование элемента события. Проверка принадлежности к событию
        и перезапись всех файлов"""
        query = f"""
        update events  
        set {edit_object} = %s
        where event_id in (
        select e.event_id 
        from events e 
        join user_event ue  
        on e.event_id = ue.event_id
        where ue.user_id = %s and ue.event_id = %s
        )
        """
        data = (new_edit_object, chat_id, id_of_event)

        try:
            Calendar.create_connection_with_database()
            with cls.connection.cursor() as cursor:
                cursor.execute(query, data)
                print('[INFO] database was successfully changed!')
                return f'Событие под номером {id_of_event} - изменено успешно!'
        except Exception as _err:
            print('[INFO] Error while working with PostgreSQL', '\n', _err)
            return 'Произошла ошибка при изменении события. Возможно, введен неправильный формат'
        finally:
            Calendar.close_connection_with_database()


