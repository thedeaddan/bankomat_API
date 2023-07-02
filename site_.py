from flask import Flask, jsonify, request
import sqlite3
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from datetime import datetime
import requests
import random
from datetime import date, timedelta


app = Flask(__name__)
bootstrap = Bootstrap(app)
db_name = "atm_system.db"

import logging

# Создаем объект логгера
logger = logging.getLogger(__name__)

# Устанавливаем уровень логгирования (можно настроить)
logger.setLevel(logging.INFO)

# Создаем объект обработчика, который записывает логи в файл
handler = logging.FileHandler('errors.log')

# Устанавливаем уровень логгирования обработчика
handler.setLevel(logging.INFO)

# Создаем форматтер для логгирования
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Устанавливаем форматтер для обработчика
handler.setFormatter(formatter)
 
# Добавляем обработчик в логгер
logger.addHandler(handler)


import random
import string

def generate_account_number():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    while True:
        # Generate a random account number
        account_number = ''.join(random.choices(string.digits, k=10))

        # Check if the account number already exists in the database
        cursor.execute("SELECT id FROM users WHERE account_number=?", (account_number,))
        result = cursor.fetchone()
        if result is None:
            # Account number is unique
            break

    conn.close()
    return account_number

@app.route("/transfer", methods=["POST"])
def money_send():
    try:
        operation_data = request.json
        account_number = operation_data["sender"]
        receiver = operation_data["reciever"]
        value = int(operation_data["value"])
    except ValueError as e:
        return jsonify({"message": "Сумма перевода не является числом " + str(e)})

    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
        balance_sender = cursor.fetchone()
        
        if not balance_sender:
            return jsonify({"message": "Недостаточно средств или пользователь не существует."})
        
        balance_sender = int(balance_sender[0])
        
        if value > balance_sender:
            create_operation(account_number, "Транзакция", f"Списание на сумму {value} отклонено. Причина: Недостаточно средств.")
            return jsonify({"message": "На счёте отправителя недостаточно средств."})
        elif value < 0:
            return jsonify({"message": "Сумма не может быть меньше нуля."})

        cursor.execute("SELECT balance FROM users WHERE account_number = ?", (receiver,))
        rec_balance = cursor.fetchone()

        if not rec_balance:
            return jsonify({"message": "Пользователя, которому вы отправляете деньги, не существует."})

        rec_balance = int(rec_balance[0])
        balance_sender -= value
        rec_balance += value

        try:
            cursor.execute("BEGIN")
            cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", (balance_sender, account_number))
            cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", (rec_balance, receiver))
            conn.commit()
            create_operation(account_number, "Транзакция", f"Списание средств {value}р. На счет {receiver}")
            create_operation(receiver, "Транзакция", f"Пополнение счёта на {value}р. От {account_number}")
            return jsonify({"message": f"Успешный перевод на сумму {value} с счёта {account_number} на счёт {receiver}"})
        except Exception as e:
            conn.rollback()
            return jsonify({"message": "Ошибка при выполнении перевода: " + str(e)})

@app.route("/add_money", methods=["POST"])
def add_money():
    try:
        operation_data = request.json
        account_number = operation_data["account_number"]
        value = int(operation_data["value"])
        
        if value < 0:
            return jsonify({"message": "Сумма не может быть меньше нуля."})
        
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE account_number = ?", (account_number,))
            balance = cursor.fetchone()
            
            if not balance:
                return jsonify({"message": "Пользователь не существует."})
            
            balance = int(balance[0])
            balance += value

            try:
                cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", (balance, account_number))
                conn.commit()
                create_operation(account_number, "Транзакция", f"Пополнение счёта на {value} р.")
                return jsonify({"message": f"Успешное пополнение счёта {account_number} на {value}р."})
            except Exception as e:
                conn.rollback()
                return jsonify({"message": "Ошибка пополнения: " + str(e)})
    except ValueError as e:
        return jsonify({"message": "Сумма перевода не является числом: " + str(e)})

@app.route('/')
def index():
    return render_template('index.html')


###ОПЕРАЦИИ###
# Получить список всех операций пользователя
@app.route("/users/<int:user_id>/operations", methods=["GET"])
def get_operations(user_id):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        if user_id == 0:
            cursor.execute("SELECT * FROM operations")
        else:
            cursor.execute("SELECT * FROM operations WHERE id=?", (user_id,))
        operations = cursor.fetchall()
        conn.close()
        return jsonify(operations)
    except Exception as e:
        logger.error('Error occurred: %s', str(e))


def create_operation(user_id, type_, description):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Generate the current date and time
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO operations (user_id, type, description, date) VALUES (?, ?, ?, ?)",
                       (user_id, type_, description, date))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error('Error occurred: %s', str(e))

# Удалить операцию
@app.route("/users/<int:user_id>/operations/<int:operation_id>", methods=["DELETE"])
def delete_operation(user_id, operation_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM operations WHERE id=? AND user_id=?", (operation_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Operation deleted successfully"})


###ВАЛЮТЫ####
# Получить список всех валют
@app.route("/currencies", methods=["GET"])
def get_currencies():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM currencies")
    currencies = cursor.fetchall()
    conn.close()
    return jsonify(currencies)

# Создать новую валюту
@app.route("/currencies", methods=["POST"])
def create_currency():
    url = "https://open.er-api.com/v6/latest/RUB"
    response = requests.get(url)
    rates = response.json()["rates"]
    print(rates)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM currencies")
    for rate,value in rates.items():
        cursor.execute("INSERT INTO currencies(name,exchange_rate) VALUES (?,?)", (rate, value))
    conn.commit()
    conn.close()
    return jsonify({"message": "Валюты успешно обновлены."})

#Удалить валюту
@app.route("/currencies/int:currency_id", methods=["DELETE"])
def delete_currency(currency_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM currencies WHERE id=?", (currency_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Валюта успешно удалена"})

###КАРТЫ###

# Получить список карт
@app.route("/cards", methods=["GET"])
def get_cards():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards")
    cards = cursor.fetchall()
    conn.close()
    return jsonify(cards)

# Создать новую карту
@app.route("/cards", methods=["POST"])
def create_card_resp():
    card_data = request.json
    create_card(card_data["user_id"], card_data["type"])

def create_card(user_id,type_):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    random_card_data = generate_random_card_data()

    cursor.execute("INSERT INTO cards (user_id, card_number, expiry_date, cvv, type) VALUES (?, ?, ?, ?, ?)",
                   (user_id,random_card_data["card_number"],random_card_data["expiry_date"],random_card_data["cvv"],type_))
    conn.commit()
    conn.close()
    create_operation(user_id, "Системное сообщение", f"Создана карта {random_card_data["card_number"]}")
    return jsonify({"message": f"Карта {random_card_data["card_number"]} создана."})

# Удалить карту
@app.route("/cards/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card deleted successfully"})

# Генерация случайного номера карты
def generate_card_number():
    card_number = ""
    for _ in range(4):
        card_number += str(random.randint(1000, 9999)) + " "
    return card_number.strip()

# Генерация случайной даты действия карты
def generate_expiry_date():
    current_date = date.today()
    expiry_date = current_date + timedelta(days=random.randint(1, 365 * 5))
    return expiry_date.strftime("%m/%Y")

# Генерация случайного CVV-кода
def generate_cvv():
    return str(random.randint(100, 999))

# Проверка наличия карты в базе данных
def check_card_exists(card_number):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE card_number = ?", (card_number,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False
    else:
        return True

# Генерация случайных данных банковской карты
def generate_random_card_data():
    while True:
        card_number = generate_card_number()
        if not check_card_exists(card_number):
            break
    
    expiry_date = generate_expiry_date()
    cvv = generate_cvv()

    return {
        "card_number": card_number,
        "expiry_date": expiry_date,
        "cvv": cvv
    }





###ПОЛЬЗОВАТЕЛИ###

# Обработчик запроса на получение списка пользователей
@app.route("/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Обработчик запроса на создание нового пользователя
@app.route("/users", methods=["POST"])
def create_user():
    print(request)
    user_data = request.json
    print(request.json)
    conn = sqlite3.connect(db_name)
    account_number = generate_account_number()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (account_number, first_name, last_name, pin, balance) VALUES (?, ?, ?, ?, ?)",
                   (account_number,user_data["first_name"], user_data["last_name"], user_data["pin"], user_data["balance"]))
    conn.commit()
    new_user_id = cursor.lastrowid
    cursor.execute("SELECT account_number FROM users WHERE id=?", (new_user_id,))
    new_user_ab = cursor.fetchone()[0]
    create_operation(new_user_ab, "Системное сообщение", f"Пользователь создан.")
    conn.close()
    return jsonify({"id": new_user_ab})

# Обработчик запроса на получение информации о конкретном пользователе
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE account_number=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return jsonify(user)

# Обработчик запроса на обновление информации о конкретном пользователе
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user_data = request.json
    print(user_data)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET first_name=?, last_name=?, pin=?, balance=? WHERE id=?",
                   (user_data["first_name"], user_data["last_name"], user_data["pin"], user_data["balance"], user_id))
    conn.commit()
    conn.close()
    return "", 204

# Обработчик запроса на удаление пользователя
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Проверка наличия пользователя в базе
    cursor.execute("SELECT id FROM users WHERE account_number=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "Пользователя нет", 404

    # Удаление пользователя из базы
    cursor.execute("DELETE FROM users WHERE account_number=?", (user_id,))
    conn.commit()
    conn.close()
    create_operation(user_id, "Системное сообщение", f"Пользователь удалён.")
    return "", 204

###БАНКОМАТЫ###

# Получить список банкоматов
@app.route("/atm", methods=["GET"])
def get_atm():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM atm")
    atm = cursor.fetchall()
    conn.close()
    return jsonify(atm)

# Создать новый банкомат
@app.route("/atm", methods=["POST"])
def create_atm():
    atm_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO atm (location, cash) VALUES (?, ?)",
                   (atm_data["location"], atm_data["cash"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "ATM created successfully"})

# Обновить информацию о банкомате
@app.route("/atm/<int:atm_id>", methods=["PUT"])
def update_atm(atm_id):
    atm_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE atm SET location=?, cash=? WHERE id=?",
                   (atm_data["location"], atm_data["cash"], atm_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "ATM updated successfully"})

# Удалить банкомат
@app.route("/atm/<int:atm_id>", methods=["DELETE"])
def delete_atm(atm_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM atm WHERE id=?", (atm_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "ATM deleted successfully"})



# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5050)
