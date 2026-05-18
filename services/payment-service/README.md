# Payment Service

Payment Service - микросервис для обработки платежей в системе e-commerce.

## Архитектура

Сервис следует **Clean Architecture** паттерну и состоит из слоёв:

- **Domain Layer** - бизнес-логика и исключения
- **Application Layer** - use cases и schemas
- **Infrastructure Layer** - database и HTTP клиенты  
- **Interfaces Layer** - API endpoints и dependencies

## Структура проекта

```
payment-service/
├── app/
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py          # Payment, PaymentStatus, PaymentMethod
│   │   ├── exceptions.py       # Исключения
│   │   ├── repositories.py     # Интерфейсы репозиториев
│   │   └── services.py         # Бизнес-логика (валидация)
│   ├── application/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── use_cases.py        # Use cases (создание, обработка платежей)
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database.py         # Pool управление
│   │   ├── repositories.py     # Реализация репозиториев
│   │   └── http_clients.py     # Клиенты для других сервисов
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Dependency injection
│   │   └── router.py           # API endpoints
│   └── main.py                 # FastAPI приложение
├── requirements.txt
└── Dockerfile
```

## API Endpoints

### Создание платежа
```
POST /payments
Content-Type: application/json
Authorization: Bearer {token}

{
  "order_id": 1,
  "amount": 5000.00,
  "currency": "KZT",
  "method": "card"
}

Ответ:
{
  "id": 1,
  "user_id": 1,
  "order_id": 1,
  "amount": 5000.00,
  "currency": "KZT",
  "status": "pending",
  "method": "card",
  "transaction_id": "TXN-...",
  "created_at": "2024-...",
  "updated_at": "2024-..."
}
```

### Получение всех платежей
```
GET /payments
Authorization: Bearer {token}

Ответ:
{
  "payments": [...]
}
```

### Получение платежа по ID
```
GET /payments/{payment_id}
Authorization: Bearer {token}
```

### Обработка платежа
```
POST /payments/{payment_id}/process
Authorization: Bearer {token}

Ответ:
{
  "payment_id": 1,
  "status": "completed",
  "transaction_id": "TXN-...",
  "updated_at": "2024-..."
}
```

### Возврат платежа
```
POST /payments/{payment_id}/refund
Authorization: Bearer {token}

Ответ:
{
  "payment_id": 1,
  "status": "refunded",
  "transaction_id": "TXN-...",
  "updated_at": "2024-..."
}
```

## Статусы платежей

- `pending` - ожидание обработки
- `completed` - успешно завершён
- `failed` - ошибка при обработке
- `refunded` - возвращён

## Методы платежа

- `card` - карта
- `bank_transfer` - банковский перевод
- `wallet` - электронный кошелёк

## Запуск

### Docker

```bash
docker build -t payment-service .
docker run -e DATABASE_URL="postgresql+asyncpg://user:password@postgres:5432/app_db" \
           payment-service
```

### Локально

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Переменные окружения

- `DATABASE_URL` - URL PostgreSQL БД (по умолчанию: `postgresql+asyncpg://user:password@postgres:5432/app_db`)

## Зависимости

Смотрите [requirements.txt](requirements.txt)

## Интеграция с другими сервисами

Payment Service взаимодействует с:

- **Order Service** - проверка существования заказа перед созданием платежа

## Frontend интеграция

### API клиент

```javascript
import { 
  createPayment, 
  getAllPayments, 
  getPayment, 
  processPayment, 
  refundPayment 
} from './api/payments.js'
```

### Компонент страницы

Страница платежей находится в [src/pages/Payments.jsx](../frontend/src/pages/Payments.jsx)

Функции:
- Просмотр всех платежей
- Создание нового платежа для заказа
- Обработка платежа (изменение статуса на completed/failed)
- Возврат платежа

## Примеры

### Создание платежа

```javascript
const payment = await createPayment(
  order_id = 1,
  amount = 5000.00,
  currency = 'KZT',
  method = 'card'
)
```

### Обработка платежа

```javascript
const result = await processPayment(payment_id = 1)
// Имитирует обработку платежа (90% успешность)
```

### Возврат платежа

```javascript
const result = await refundPayment(payment_id = 1)
// Доступно только для завершённых платежей
```

## Notes

- При создании платежа автоматически генерируется уникальный Transaction ID
- Обработка платежа имитирует 90% успешность (для демо)
- Переходы между статусами контролируются бизнес-логикой
- Все сумма хранятся в виде Decimal для точности
