import psycopg2
import json
import configparser

#from READY import host,user,password,db_name,port
#configParser


config = configparser.ConfigParser()
config.read("config.txt")

host = config.get("POSTGRES", "host")
user = config.get("POSTGRES", "user")
password = config.get("POSTGRES", "password")
db_name = config.get("POSTGRES", "db_name")
port = config.get("POSTGRES", "port")

delete_table = config.getboolean("POSTGRES", "delete_table")


print(user)
print(host)
print(password)
print(db_name)
print(db_name)
print("delete_table = ", delete_table)

# host = config.read("host
# user = "postgres"
# password = "1337"
# db_name = "postgres"
# port = 5433


def load_user_data(user_id):
    # загрузка юзеров из toggleuserjs.json
    with open("toggleusers.json", "r") as json_file:
        data = json.load(json_file)
        for entry in data:
            if entry["user_id"] == user_id:
                return entry

    return {}  


def postgres_toggle(report_toggle_path, toggle_table_name):
    
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        print(f"Подклчение к таблице {toggle_table_name} выполнено")
        cursor = connection.cursor()
        
        if delete_table:
            # получаем из конфига условие по обновлению/добавлению таблицы
            drop_sql = f"DROP TABLE IF EXISTS {toggle_table_name} CASCADE"
            cursor.execute(drop_sql)
            connection.commit()
            print(f'удаление таблицы {toggle_table_name} выполнено')
        
        create = f"""
        CREATE TABLE IF NOT EXISTS {toggle_table_name}  
        (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    username TEXT,
                    email TEXT,
                    project_id INTEGER,
                    project_name TEXT,
                    description TEXT,
                    time_id BIGINT,
                    seconds INTEGER,
                    start_time TEXT,
                    stop_time TEXT,
                    mins INTEGER,
                    normal_time TEXT
        )
        """
        cursor.execute(create)
        connection.commit()
        print(f'Таблица {toggle_table_name} создана')

        with open(report_toggle_path, "r") as json_file:
            data = json.load(json_file)
            
            for entry in data:
                user_id = entry["user_id"]
                username = entry["username"]
                project_id = entry["project_id"]
                project_name = entry["project_name"]
                description = entry["description"]
                user_data = load_user_data(user_id)
                for times in entry["time_entries"]:
                    time_id = times["id"]
                    seconds = times["seconds"]
                    start_time = times["start"]
                    stop_time = times["stop"]
                    normal_time = times["normal_time"]
                    mins = times["mins"]
                    email = user_data["email"]
                    
                    # SQL INSERT
                    insert_sql = f"""
                    INSERT INTO {toggle_table_name} (user_id, username, email, project_id, project_name, description, time_id, seconds, start_time, stop_time, mins, normal_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_sql, (user_id, username, email, project_id, project_name, description, time_id, seconds, start_time, stop_time, mins, normal_time))
                    connection.commit()
                    
    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Подключение к таблице postgres закрыто")

def create_kaiten_times_table(kaiten_times_table_name, kaiten_times_json_path):
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        cursor = connection.cursor()
        if delete_table:
        # Удаляем табилцу если существует в базе
            drop_sql = f"DROP TABLE IF EXISTS {kaiten_times_table_name} CASCADE"
            cursor.execute(drop_sql)
            connection.commit()
        
        # Создаем таблицу
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {kaiten_times_table_name} (
            id SERIAL PRIMARY KEY,
            card_id BIGINT,
            username TEXT,
            time_spent INTEGER,
            total_sum_with_hours TEXT,
            role TEXT,
            customer TEXT,
            created TIMESTAMP,
            total_time INTEGER,
            comment TEXT
            
        )
        """

        cursor.execute(create_sql)
        print(f'Таблица {kaiten_times_table_name} создана')

        # Читаем данные из джсона и заполняем (structured_time.json)
        with open(kaiten_times_json_path, "r") as json_file:
            structured_time_data = json.load(json_file)
            
            for card_id, card_data in structured_time_data["time_logs_data"].items():
                for username, user_data in card_data.items():
                    time_spent = user_data["Time_spent"][0]["time_spent"]
                    total_sum_with_hours = user_data["Total_sum_with_hours"]
                    role = user_data["Role"]
                    customer = user_data["Customer"]
                    created = user_data["Time_spent"][0]["created"]
                    comment = user_data["Time_spent"][0]["comment"]
                    #total_sum = user_data["Total_sum"]
                
                    # SQL ISNERT 
                    insert_sql = f"""
                    INSERT INTO {kaiten_times_table_name} (card_id, username, time_spent, total_sum_with_hours, role, customer, created, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # исключение
                    cursor.execute(insert_sql, (card_id, username, time_spent, total_sum_with_hours, role, customer, created, comment))

            for card_id, total_time in structured_time_data["total_time_per_card"].items():
                update_sql = f"""
                UPDATE {kaiten_times_table_name}
                SET total_time = %s
                WHERE card_id = %s
                """
                cursor.execute(update_sql, (total_time, card_id))
            
            
        connection.commit()
        print("Data_kaiten таблица успешно создана в postgres")
        
    except Exception as ex:
        print("[INFO] Ошибка подключения к PostgreSQL:", ex)
    

def update_comments_in_table(kaiten_data_tabble_name, comments_json_path):
    print("update_comments_in_table выполнение начато")
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        cursor = connection.cursor()

        # читаем комменты из дсжона
        with open(comments_json_path, "r", encoding="utf-8") as json_file:
            comments_data = json.load(json_file)

        for card_id, comment in comments_data.items():
            # апдейт таблицы
            update_sql = f"""
            UPDATE {kaiten_data_tabble_name}
            SET comment = %s
            WHERE card_id = %s
            """
            cursor.execute(update_sql, (comment, card_id))

        connection.commit()
        print("Поле comments успешно обновлено")

    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("create_kaiten_times_table соединение закрыто")

#dataKaiten.json
def create_data_kaiten_table(kaiten_data_tabble_name, kaiten_data_json_path):
    connection = None
    cursor = None
    
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        cursor = connection.cursor()
        
        drop_sql = f"DROP TABLE IF EXISTS {kaiten_data_tabble_name} CASCADE"
        cursor.execute(drop_sql)
        connection.commit()
        
        create_sql = f"""
        CREATE TABLE {kaiten_data_tabble_name} (
            id SERIAL PRIMARY KEY,
            Card_id INTEGER,
            Card_Name TEXT,
            username TEXT,
            User_email TEXT,
            User_role TEXT,
            comment TEXT,
            space TEXT,
            time INTEGER,
            Time_spent_with_hours TEXT
        )
        """
        cursor.execute(create_sql)
        print(f"Таблица {kaiten_data_tabble_name} создана")
        
        with open(kaiten_data_json_path, "r") as json_file:
            data_kaiten = json.load(json_file)
            
            for card_data in data_kaiten:
                card_id = card_data["Card ID"]
                card_name = card_data["Card Name"]
                username = card_data["User"]
                user_email = card_data["User's Email"]
                user_role = card_data["User Role"]
                comment = card_data["Comment"]
                space = card_data["Space"]
                time = card_data["Time_spent"]
                time_spent_with_hours = card_data["Time_spent_with_hours"]
                
                insert_sql = f"""
                INSERT INTO {kaiten_data_tabble_name} (Card_id, Card_Name, username, User_email, User_role, comment, space, time, Time_spent_with_hours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (card_id, card_name, username, user_email, user_role, comment, space, time, time_spent_with_hours))
                connection.commit()
        
        print(f"{kaiten_data_tabble_name} таблица успешно создана в postgres")
        
    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("create_data_kaiten_table функция соединение закрыто")


# kaiten_data_tabble_name = "data_kaiten"
# kaiten_data_json_path = "dataKaiten.json"
# create_data_kaiten_table(kaiten_data_tabble_name, kaiten_data_json_path)
# report_toggle_path = 'report_toggle.json'
# toggle_table_name = 'toggl'
# postgres_toggle(report_toggle_path, toggle_table_name)