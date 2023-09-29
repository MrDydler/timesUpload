# timesUpload
Выгружает файлы из сервисов toggle и kaiten в .json и записывает их в postgresql

Для запуска скрипта потребуется создать config.txt файле в корне с .py файлами

Заполянем их следующими данными по сервисам

Uploads files from toggle and kaiten services to .json and writes them to postgresql

To run the script, you will need to create config.txt a file in the root with .py files

Fill them with the following data on services


[POSTGRES]
user = postgres
password = 1337
db_name = time
host = 127.0.0.1
port = 5432
delete_table = True


[DEFAULT]
toggle_login = toggle email
toggle_pass = pass
start_date = 2023-09-25
end_date = 2023-09-27
api_key = 432423423423423423423
user_ids = 7185973, 8431059, 7819625, 9323244, 8738288, 8209137, 8829962, 7819625, 8431059, 9273122, 7032326
