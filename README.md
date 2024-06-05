# fastapi_other_code_test
Инструкции по развертыванию проекта

Для развертывания понадобится Docker и Docker Compose.

Клонирование репозитория

Сначала клонируйте репозиторий проекта на ваш локальный компьютер с помощью git:

git clone https://github.com/Ignntbc/fastapi_other_code_test.git

Общий проект

Проект можно развернуть находясь в корневой папке проекта с помощью команды

docker-compose up -d --build

При этом будут подняты все необходимые контейнеры (redis, postgres, alembic, web, tests).
Применятся миграции к базе данных, будут запущены автотесты, и развернется основной проект
который будет слушать на порту 90. Рекомендуется сначала развернуть базу данных, после 
применить к ней миграции, и после этого запускать тесты.

База данных и миграции
Для запуска базы данных и выполнения миграций используйте следующую команду:

docker-compose up -d --build db

После удачного запуска базы даннных применяем миграции

docker-compose up -d --build alembic

Контейнер alembic выполнит миграции в базе данных.

Запуск тестов
Для запуска тестов используйте следующую команду:

docker-compose up -d --build tests

Это запустит контейнер tests, который выполнит все тесты в файле tests.py.

Запуск основного проекта
Для запуска основного проекта используйте следующую команду:

docker-compose up -d --build web

Это запустит контейнер web, который будет слушать на порту 90.
