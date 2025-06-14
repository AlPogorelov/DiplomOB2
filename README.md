# Дипломный проект OB2
Платформа предоставляет инструменты для быстрой публикации контента
и его монетизации через микротранзакции, сохраняя баланс между доступностью
и безопасностью. Использование Bootstrap и Stripe ускоряет разработку,
а упрощенная регистрация повышает вовлеченность аудитории.

# IP ВМ 158.160.3.141
## Локальная установка и запуск

### Требования
- Docker 20.10+
- docker-compose 1.29+

### Запуск проекта
1. Клонируйте репозиторий:
```
git clone https://github.com/AlPogorelov/DiplomOB2.git
cd /var/www/DiplomOB2
```

### Заполните значения в файле .env:

```
SECRET_KEY =
DEBUG = True
POSTGRES_DB =
POSTGRES_USER =
POSTGRES_PASSWORD =
POSTGRES_HOST =
POSTGRES_PORT =

STRIPE_API_KEY =
STRIPE_PUBLISHABLE_KEY =

```
### Запустите проект:
```docker-compose up --build```

Проект будет доступен по адресу: http://158.160.3.141

# Настройка CI/CD
## Требования
Сервер с Docker

SSH доступ к серверу

Аккаунт на Docker Hub

## Инструкция
### Добавьте секреты в GitHub (Settings → Secrets):
SECRET_KEY - секретный ключ Django

POSTGRES_* - данные PostgreSQL

DOCKER_HUB_USERNAME - логин Docker Hub

DOCKER_HUB_ACCESS_TOKEN - токен Docker Hub

SSH_KEY - приватный SSH-ключ

SSH_USER - пользователь сервера

SERVER_IP - IP сервера

## Настройте сервер:
Установите Docker

```sudo apt-get update && sudo apt-get install docker.io docker-compose```

Добавьте пользователя в группу docker
```
sudo usermod -aG docker $USER
newgrp docker
```
## При пуше произойдет:

Линтинг кода

Запуск тестов

Сборка Docker-образов

Пуш образов в Docker Hub

Автоматический деплой на сервер

