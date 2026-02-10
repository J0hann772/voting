# hard second project



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.informatics.ru/2025-2026/hse/s102m/hard-second-project.git
git branch -M main
git push -uf origin main
```
# 🚀 Инструкция по локальному запуску (Docker)
## 1. Подготовка (один раз)
Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Запустите приложение Docker Desktop на компьютере.

(Опционально) Если Docker попросит, зарегистрируйтесь

## 2. Первый запуск
Откройте терминал в папке проекта и выполните команду:



```
docker-compose up --build
```
Дождитесь, пока установятся зависимости и появится надпись Starting development server at ....

Внимание: Не закрывайте это окно терминала, сервер работает в нем.


## 3. Настройка базы данных (во втором терминале)
Пока сервер работает в первом окне, откройте второе окно терминала и выполните первичную настройку:



### Применяем миграции (создаем таблицы)
```
docker-compose exec web python manage.py migrate
```

### Создаем админа (придумайте логин и пароль)
```
docker-compose exec web python manage.py createsuperuser
```

Проект доступен по адресу: http://127.0.0.1:8000

## 🛠 Повседневная работа
Как работать с кодом: Просто меняйте код в своем редакторе и сохраняйте файлы. Docker автоматически увидит изменения и перезагрузит сервер (Hot Reload). Перезапускать контейнер вручную не нужно.

Как применять новые миграции: Если кто-то (или вы) изменил модели, выполните во втором окне:

```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

Как остановить сервер: В окне, где запущен сервер, нажмите Ctrl + C.

Полезные команды:

```
docker-compose up
```
— просто запустить (быстрее, если не меняли requirements.txt).

```
docker-compose up --build
```
— запустить с пересборкой (если меняли requirements.txt).

```
docker-compose exec web python -m sphinx.cmd.build -b html docs/source static/docs
```
— запустить пересборку html документации после изменения.

