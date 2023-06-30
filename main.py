import sqlite3

# подключаемся к базе данных
conn = sqlite3.connect('bank.db')

# создаем курсор для выполнения запросов
cursor = conn.cursor()

# выбираем все записи из таблицы "users"
cursor.execute("SELECT * FROM users")

# получаем все строки из результата запроса
rows = cursor.fetchall()

# выводим результаты
for row in rows:
    print(f"ID: {row[0]}\nИмя: {row[1]}\nФамилия: {row[2]}\nПочта: {row[3]}\nПароль: {row[4]}\n")

# закрываем соединение с базой данных
conn.close()

