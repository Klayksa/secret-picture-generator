# ImageGenerator

Данный проект является частью (сервисом) решения кейса с [**VTB API Hackathon 2024**](https://apihack.vtb.ru/) от команды **"Пожилая ряженка"** (здесь нет смысла, не пытайтесь его найти, мы до сих пор не знаем что на это сказать, так получилось)

Сервис предоставляет собой API для генерации изображений с помощью FusionBrain AI, с последующим скрытием секретного сообщения в изображении с использованием стеганографии.

## Основные возможности

- Генерация изображений по текстовому описанию (prompt) через FusionBrain API
- Встраивание секретного сообщения в изображение с помощью стеганографии
- Проверка статуса генерации изображения
- Извлечение скрытого сообщения из изображения

## Установка и запуск


1. Установите в виртуальное окружение (без него не советую) зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Настройте переменные окружения (создайте файл `.env`, пример в `.env_dev`):
   ```ini
   FUSION_BRAIN_API_KEY=ваш_api_ключ
   FUSION_BRAIN_SECRET_KEY=ваш_secret_ключ
   ENCRIPTION_KEY=Fernet.generate_key()
   REDIS_URL=redis://localhost:6379/0
   ```

3. Запустите проект с помощью docker-compose:
   ```
    docker-compose up
   ```

   Пример `docker-compose` из проекта:
   ```
    services:

    redis:
        container_name: redis
        image: redis:7.4.1-alpine

    image-authentification:
        container_name: image-authentification
        build: ./ImageAuthentification
        command: sh -c "gunicorn ImageAuthentification.wsgi:application --bind 0.0.0.0:8000"
        ports:
        - 8000:8000
        depends_on:
        - redis

    celery:
        container_name: celery
        build: ./ImageAuthentification
        command: sh -c "celery -A ImageAuthentification worker -l info"
        depends_on:
        - redis
   ``` 

## API Endpoints

### 1. Генерация изображения
`POST /api/generate/`

**Параметры:**
- `promt` - описание для генерации изображения
- `style` - стиль изображения (из доступных в FusionBrain)
- `secret` - секретное сообщение для встраивания

**Ответ:**
```json
{"TASK_ID": "uuid-задачи"}
```

### 2. Проверка статуса генерации
`GET /api/check/<uuid_задачи>/`

**Ответ:**
```json
{
  "STATUS": "GENERATE|DONE",
  "IMAGE": "base64_изображения" (если статус DONE)
}
```

### 3. Извлечение секрета из изображения
`POST /api/decode/`

**Параметры:**
- `image` - изображение в формате base64

**Ответ:**
Секретное сообщение (текст) или ошибка

## 🛠 Технологии

- Python 3.11
- Django 5.1.2
- Celery + Redis
- FusionBrain AI API v1
