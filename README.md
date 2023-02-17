Банкомат
========

Это проект информационной системы банкомата. Проект включает в себя базу данных на SQLite и API на Python и Flask.

Структура базы данных
---------------------

База данных состоит из следующих таблиц:

*   `users`: информация о пользователях
*   `cards`: информация о картах, привязанных к пользователям
*   `transactions`: история транзакций, связанных с картами
*   `operations`: информация об операциях, доступных на банкомате
*   `atm`: информация о банкоматах
*   `exchange_rates`: информация о курсах валют
*   `currencies`: информация о доступных валютах

Установка
---------

1.  Клонировать репозиторий
2.  Создать виртуальное окружение: `python -m venv venv`
3.  Активировать виртуальное окружение:
    *   Windows: `venv\Scripts\activate.bat`
    *   Linux/Mac: `source venv/bin/activate`
4.  Установить зависимости: `pip install -r requirements.txt`
5.  Запустить сервер: `python site_.py`

Использование
-------------

### API для пользователей

#### Получить список пользователей

`GET /users`

Возвращает список всех пользователей.

#### Получить пользователя

`GET /users/<int:user_id>`

Возвращает информацию о пользователе с заданным `user_id`.

#### Создать пользователя

`POST /users`

Создает нового пользователя. В теле запроса необходимо указать JSON с полями `name`, `email`, `password`.

#### Обновить пользователя

`PUT /users/<int:user_id>`

Обновляет информацию о пользователе с заданным `user_id`. В теле запроса необходимо указать JSON с полями `name`, `email`, `password`.

#### Удалить пользователя

`DELETE /users/<int:user_id>`

Удаляет пользователя с заданным `user_id`.

### API для карт

#### Получить список карт

`GET /cards`

Возвращает список всех карт.

#### Получить карту

`GET /cards/<int:card_id>`

Возвращает информацию о карте с заданным `card_id`.

#### Создать карту

`POST /cards`

Создает новую карту. В теле запроса необходимо указать JSON с полями `user_id`, `card_number`, `expiry_date`, `cvv`, `balance`, `currency_id`.

#### Обновить карту

`PUT /cards/<int:card_id>`

Обновляет информацию о карте с заданным `card_id`. В теле запроса необходимо указать JSON с полями `user_id`, `card_number`, `expiry_date`, `cvv`, `balance`, `currency_id`.

#### Удалить карту

`DELETE /cards/<int:card_id>`

Удаляет карту с заданным `card_id`.

### API для транзакций

#### Получить список транзакций

`GET /transactions`

Возвращает список всех транзакций.

### API для операций

#### Получить список операций

`GET /operations`

Возвращает список всех операций.

#### Получить операцию

`GET /operations/<int:operation_id>`

Возвращает информацию об операции с заданным `operation_id`.

#### Создать операцию

`POST /operations`

Создает новую операцию. В теле запроса необходимо указать JSON с полями `name`, `description`.

#### Обновить операцию

`PUT /operations/<int:operation_id>`

Обновляет информацию об операции с заданным `operation_id`. В теле запроса необходимо указать JSON с полями `name`, `description`.

#### Удалить операцию

`DELETE /operations/<int:operation_id>`

Удаляет операцию с заданным `operation_id`.

### API для банкоматов

#### Получить список банкоматов

`GET /atm`

Возвращает список всех банкоматов.

#### Получить банкомат

`GET /atm/<int:atm_id>`

Возвращает информацию о банкомате с заданным `atm_id`.

#### Создать банкомат

`POST /atm`

Создает новый банкомат. В теле запроса необходимо указать JSON с полями `name`, `location`.

#### Обновить банкомат

`PUT /atm/<int:atm_id>`

Обновляет информацию о банкомате с заданным `atm_id`. В теле запроса необходимо указать JSON с полями `name`, `location`.

#### Удалить банкомат

`DELETE /atm/<int:atm_id>`

Удаляет банкомат с заданным `atm_id`.


