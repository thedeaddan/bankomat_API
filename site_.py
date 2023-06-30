from flask import Flask, jsonify, request
import sqlite3
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
db_name = "atm_system.db"

import logging

# Создаем объект логгера
logger = logging.getLogger(__name__)

# Устанавливаем уровень логгирования (можно настроить)
logger.setLevel(logging.ERROR)

# Создаем объект обработчика, который записывает логи в файл
handler = logging.FileHandler('errors.log')

# Устанавливаем уровень логгирования обработчика
handler.setLevel(logging.ERROR)

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
    operation_data = request.json
    account_number= operation_data["sender"]
    reciever=operation_data["reciever"]
    try:
        value=int(operation_data["value"])
    except:
         return jsonify({"message": "Сумма перевода не является числом"})
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE account_number = ?",(account_number,))
    bal = cursor.fetchone()
    try:
        balace_sender = int(bal[0])
        if value > balace_sender:
            create_operation(account_number, "Транзакция", f"Списание на сумму {value} отклонено. Причина: Недостаточно средств.")
            return jsonify({"message":"На счёте отправителя недостаточно средств."})
        elif value < 0:
            return jsonify({"message":"Сумма не может быть меньше нуля."})
        else:
            cursor.execute("SELECT balance FROM users WHERE account_number = ?",(reciever,))
            rec_bal = cursor.fetchone()
            try:
                rec_bal = int(rec_bal[0])
                balace_sender = balace_sender - value
                cursor.execute("UPDATE users SET balance=? WHERE account_number =? ",(balace_sender,account_number,))
                rec_bal = rec_bal + value
                cursor.execute("UPDATE users SET balance=? WHERE account_number =? ",(rec_bal,reciever,))
                conn.commit()
                conn.close()
                create_operation(account_number, "Транзакция", f"Списание средств {value}р. На счет {reciever}")
                create_operation(reciever, "Транзакция", f"Пополнение счёта на {value}р. От {account_number}")
                return jsonify({"message":f"Успешный перевод на сумму {value} с счёта {account_number} на счёт {reciever}"})
            except Exception as e:
                return jsonify({"message":"Пользователя которому вы отправляете деньги не существует. Или ошибка "+str(e)})
    except:
        return jsonify({"message": "Недостаточно средств или пользователь не существует."})

@app.route("/add_money", methods=["POST"])
def add_money():
    operation_data = request.json
    account_number = operation_data["account_number"]
    try:
        value=int(operation_data["value"])
        if value < 0:
            return jsonify({"message":"Сумма не может быть меньше нуля."})
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE account_number = ?",(account_number,))
        balance = cursor.fetchone()[0]
        try:
            balance = int(balance)+value
            cursor.execute("UPDATE users SET balance=? WHERE account_number =? ",(balance,account_number,))
            conn.commit()
            conn.close()
            create_operation(account_number, "Транзакция", f"Пополнение счёта на {value} р.")
            return jsonify({"message": f"Успешное пополнение счёта {account_number} на {value}р. "})
        except Exception as e:
            return jsonify({"message": "Ошибка пополнения "+e})
    except Exception as e:
        return jsonify({"message": "Сумма перевода не является числом"+str(e)})




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
    currency_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO currencies (name, code, symbol) VALUES (?, ?, ?)",
                   (currency_data["name"], currency_data["code"], currency_data["symbol"]))
    currency_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": currency_id}), 201

# Обновить информацию о валюте
@app.route("/currencies/<int:currency_id>", methods=["PUT"])
def update_currency(currency_id):
    currency_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE currencies SET name=?, code=?, symbol=? WHERE id=?",
               (currency_data["name"], currency_data["code"], currency_data["symbol"], currency_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Currency updated successfully"})

#Удалить валюту
@app.route("/currencies/int:currency_id", methods=["DELETE"])
def delete_currency(currency_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM currencies WHERE id=?", (currency_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Currency deleted successfully"})

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
def create_card():
    card_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cards (user_id, card_number, expiry_date, cvv, balance, type) VALUES (?, ?, ?, ?, ?, ?)",
                   (card_data["user_id"], card_data["card_number"], card_data["expiry_date"], card_data["cvv"], card_data["balance"], card_data["type"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card created successfully"})

# Обновить информацию о карте
@app.route("/cards/<int:card_id>", methods=["PUT"])
def update_card(card_id):
    card_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE cards SET user_id=?, card_number=?, expiry_date=?, cvv=?, balance=?, type=? WHERE id=?",
                   (card_data["user_id"], card_data["card_number"], card_data["expiry_date"], card_data["cvv"], card_data["balance"], card_data["type"], card_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card updated successfully"})

# Удалить карту
@app.route("/cards/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cards WHERE id=?", (card_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Card deleted successfully"})


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

###КУРСЫ###

# Получить список курсов валют
@app.route("/exchange_rates", methods=["GET"])
def get_exchange_rates():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exchange_rates")
    exchange_rates = cursor.fetchall()
    conn.close()
    return jsonify(exchange_rates)

# Добавить новый курс валюты
@app.route("/exchange_rates", methods=["POST"])
def create_exchange_rate():
    exchange_rate_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exchange_rates (date, base_currency, exchange_currency, exchange_rate) VALUES (?, ?, ?, ?)",
                   (exchange_rate_data["date"], exchange_rate_data["base_currency"], exchange_rate_data["exchange_currency"], exchange_rate_data["exchange_rate"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Exchange rate created successfully"})

# Обновить курс валюты
@app.route("/exchange_rates/<int:exchange_rate_id>", methods=["PUT"])
def update_exchange_rate(exchange_rate_id):
    exchange_rate_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE exchange_rates SET date=?, base_currency=?, exchange_currency=?, exchange_rate=? WHERE id=?",
                   (exchange_rate_data["date"], exchange_rate_data["base_currency"], exchange_rate_data["exchange_currency"], exchange_rate_data["exchange_rate"], exchange_rate_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Exchange rate updated successfully"})

# Удалить курс валюты
@app.route("/exchange_rates/<int:exchange_rate_id>", methods=["DELETE"])
def delete_exchange_rate(exchange_rate_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exchange_rates WHERE id=?", (exchange_rate_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Exchange rate deleted successfully"})


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5050)
