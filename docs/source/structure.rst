Структура проекта
=================

Архитектура приложения **hard-second-project**:

.. code-block:: text

   project/
   ├── config/              # Конфигурация Django
   │   ├── settings.py      # Настройки (БД, приложения, статика)
   │   ├── urls.py          # Главный маршрутизатор URL
   │   └── asgi.py/wsgi.py  # Точки входа для серверов
   ├── user/                # Приложение пользователей
   │   ├── models.py        # Модель User и Profile
   │   ├── forms.py         # Формы регистрации и профиля
   │   └── views.py         # Вьюхи (Login, Logout, Profile)
   ├── voting/              # Основное приложение голосований
   │   ├── models.py        # Сущности Voting, Choice, Vote
   │   ├── forms.py         # Форма создания опроса
   │   └── views.py         # Логика голосования
   ├── templates/           # HTML-шаблоны (base, index, profile)
   ├── Dockerfile           # Инструкция для сборки образа
   └── manage.py            # Утилита управления