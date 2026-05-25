# Food Plan

Командный проект на Django — сервис подписок на индивидуальное питание.

Пользователь выбирает тип диеты, приёмы пищи, количество персон и срок подписки. Система ежедневно генерирует персональное меню с учётом аллергий и предпочтений, а оплата проходит через ЮKassa.

## ⚙️ Технический стек

- **База данных**: PostgreSQL (через `DATABASE_URL`; SQLite по умолчанию для локальной разработки)
- **Бэкенд**: Python 3.x, Django 6.x
- **Фронтенд**: Django Templates, Bootstrap
- **Хранилище файлов**: MinIO / S3 (опционально, через `django-storages` + `boto3`)
- **Платежи**: ЮKassa (`yookassa`)
- **Конфигурация**: `django-environ`

## 📂 Структура проекта

```
.
├── core/               # Основное Django-приложение
│   ├── migrations/     # Миграции базы данных
│   ├── static/         # CSS, JS, изображения
│   ├── templates/      # HTML-шаблоны
│   ├── admin.py        # Настройки админ-панели
│   ├── forms.py        # Формы (регистрация, профиль, подписка, отзывы)
│   ├── models.py       # Модели (Recipe, Subscription, DailyMenu, …)
│   ├── services.py     # Бизнес-логика (генерация меню дня)
│   └── views.py        # Представления
├── food_plan/          # Настройки проекта (settings, urls, wsgi, storage)
├── test/               # Тестовые данные и фикстуры
├── manage.py
├── requirements.txt
└── .env.example
```

## 🧩 Основные модели

| Модель | Описание |
|---|---|
| `Recipe` | Рецепт блюда с ингредиентами, калорийностью и типом диеты |
| `Ingredient` | Ингредиент с калорийностью на 100 г и списком аллергенов |
| `Subscription` | Подписка пользователя (диета, срок, приёмы пищи, статус, оплата) |
| `DailyMenu` | Сгенерированное меню на конкретный день и приём пищи |
| `MealType` | Тип приёма пищи (завтрак, обед, ужин, …) с базовой ценой |
| `DietType` | Тип диеты (классическая, низкоуглеводная, вегетарианская, кето) |
| `SubscriptionPeriod` | Срок подписки (месяцы) и множитель цены |
| `Allergy` | Аллерген, исключаемый из меню подписки |
| `PromoCode` | Промокод с процентом скидки и периодом действия |
| `Review` | Отзыв пользователя с оценкой, текстом и фото (модерируемый) |
| `Profile` | Профиль пользователя с аватаром |

## 🔑 Основные страницы

| URL | Описание |
|---|---|
| `/` | Главная страница с отзывами |
| `/auth/` | Авторизация |
| `/registration/` | Регистрация |
| `/lk/` | Личный кабинет (профиль, подписки) |
| `/order/` | Оформление подписки |
| `/subscription/<id>/` | Детали подписки |
| `/subscription/<id>/today/` | Меню на сегодня |
| `/recipe/<id>/` | Карточка рецепта (админ) |
| `/review/create/` | Создание отзыва |
| `/payment/create/` | Создание платежа |
| `/payment/success/` | Страница успешной оплаты |
| `/payment/failure/` | Страница ошибки оплаты |
| `/admin/` | Панель администратора |

## 🛠️ Установка и Настройка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/Ann2004/food-plan.git
   cd food-plan
   ```

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения. На основе `.env.example` создайте `.env` файл:

   ```env
   # Django
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost:8000

   # Database
   DATABASE_URL=sqlite:///db.sqlite3

   # Email
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

   # MinIO / S3 (optional for local dev)
   USE_MINIO=False

   # Yookassa (optional in DEBUG=True)
   YOOKASSA_SHOP_ID=your-shop-id
   YOOKASSA_SECRET_KEY=your-secret-key
   ```

5. Примените миграции и создайте суперпользователя:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Запустите сервер:

   ```bash
   python manage.py runserver
   ```
