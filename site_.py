from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
db_name = "atm_system.db"

###ОПЕРАЦИИ###
# Получить список всех операций пользователя
@app.route("/users/<int:user_id>/operations", methods=["GET"])
def get_operations(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operations WHERE user_id=?", (user_id,))
    operations = cursor.fetchall()
    conn.close()
    return jsonify(operations)

# Создать новую операцию
@app.route("/users/<int:user_id>/operations", methods=["POST"])
def create_operation(user_id):
    operation_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO operations (user_id, type, amount, currency, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, operation_data["type"], operation_data["amount"], operation_data["currency"], operation_data["date"]))
    operation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"id": operation_id}), 201

# Обновить информацию об операции
@app.route("/users/<int:user_id>/operations/<int:operation_id>", methods=["PUT"])
def update_operation(user_id, operation_id):
    operation_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("UPDATE operations SET type=?, amount=?, currency=?, date=? WHERE id=? AND user_id=?",
                   (operation_data["type"], operation_data["amount"], operation_data["currency"], operation_data["date"], operation_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Operation updated successfully"})

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
    user_data = request.json
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (first_name, last_name, pin, balance) VALUES (?, ?, ?, ?)",
                   (user_data["first_name"], user_data["last_name"], user_data["pin"], user_data["balance"]))
    conn.commit()
    new_user_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_user_id})

# Обработчик запроса на получение информации о конкретном пользователе
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
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
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
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
    app.run(debug=True,host='0.0.0.0')
