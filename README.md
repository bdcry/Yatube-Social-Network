
***Yatube Web-blog***

---



***Описание:***

Это блог, в котором вы можете публиковать свои мысли и мнения по различным темам. Вы можете выбрать конкретную группу для своего поста. Кроме того, вы можете следить за другими авторами и просматривать сообщения от других людей.

---

***Установка:***

***1. Скопируйте репозиторий и активируйте виртуальной окружение для Windows:***

```
python -m venv venv
Source venv/Scripts/activate
```

***для Mac:***
```
python -m venv venv
Source venv/Bin/activate
```
***2. установите библиотеки(requirements.txt)***

```
pip install -r requirements.txt
```

***3. Создайте и запустите миграции:***

```
python manage.py makemigrations
python manage.py migrate
```

***4. Запустите сервер:***

```
python manage.py runserver
```

