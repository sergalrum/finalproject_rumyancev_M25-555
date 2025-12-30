# ValutaTrade Hub

**Платформа для отслеживания и симуляции торговли валютами** с поддержкой фиатных и криптовалют.

## О проекте

ValutaTrade Hub — это CLI‑приложение для:
- управления виртуальным портфелем валют;
- совершения торговых операций (покупка/продажа);
- отслеживания актуальных курсов в реальном времени;
- работы с фиатными и криптовалютами.

## Структура проекта

```
finalproject_rumyancev_M25-555/
├── data/                   # Хранилище данных
│   ├── users.json      # пользователи системы
│   ├── portfolios.json # портфели и кошельки
│   ├── rates.json     # локальный кэш текущих курсов
│   └── exchange_rates.json # исторические данные
├── logs/               # Логи приложения
│   └── actions.log
├── valutatrade_hub/    # Основной код проекта
│   ├── logging_config.py # настройка логирования
│   ├── decorators.py   # декораторы для логирования
│   ├── core/           # Бизнес‑логика
│   │   ├── currencies.py # иерархия валют
│   │   ├── exceptions.py # пользовательские исключения
│   │   ├── models.py   # модели данных (User, Wallet, Portfolio)
│   │   ├── usecases.py # бизнес‑логика операций
│   │   └── utils.py    # вспомогательные функции
│   ├── infra/          # Инфраструктура
│   │   ├── settings.py # Singleton SettingsLoader
│   │   └── database.py # Singleton DatabaseManager
│   ├── parser_service/  # Сервис парсинга курсов
│   │   ├── config.py   # конфигурация API
│   │   ├── api_clients.py # клиенты внешних API
│   │   ├── updater.py  # логика обновления курсов
│   │   └── storage.py  # работа с хранилищем
│   └── cli/
│       └── interface.py  # CLI интерфейс
├── main.py             # Точка входа
├── Makefile            # Автоматизация задач
├── pyproject.toml      # Конфигурация Poetry
└── README.md           # Документация
```

## Установка

### Требования
- Python 3.8+
- Poetry (менеджер зависимостей)

### Установка зависимостей

**Вариант 1: через Makefile**
```bash
make install
```

**Вариант 2: напрямую через Poetry**
```bash
poetry install
```

## Запуск приложения

**Вариант 1: через Makefile**
```bash
make project
```

**Вариант 2: напрямую**
```bash
poetry run python main.py
```

## Доступные команды Makefile

- `make install` — установка зависимостей через Poetry;
- `make project` — запуск проекта в интерактивном режиме;
- `make build` — сборка пакета для распространения;
- `make publish` — публикация пакета в репозиторий (если настроено);
- `make package-install` — установка собранного пакета через pip;
- `make lint` — проверка кода линтером (ruff).

## Поддерживаемые валюты

### Фиатные
- USD (базовая валюта)
- EUR
- GBP
- RUB
- JPY

### Криптовалюты
- BTC (Bitcoin)
- ETH (Ethereum)
- LTC (Litecoin)
- ADA (Cardano)

## Настройки времени жизни данных (TTL)

- Курсы считаются «свежими» в течение **300 секунд (5 минут)**.
- По истечении TTL система предлагает обновить данные.
- Настройка TTL производится в `infra/settings.py`.


## Обработка ошибок

Система обрабатывает следующие типы ошибок:
- `InsufficientFundsError` — недостаточно средств для операции;
- `CurrencyNotFoundError` — неизвестная валюта;
- `ApiRequestError` — ошибки при обращении к внешним API;
- `UserNotFoundError` — пользователь не найден;
- `InvalidPasswordError` — неверный пароль.

## Логирование

- Логи хранятся в файле `logs/actions.log`.
- Формат записи: `LEVEL TIMESTAMP LOGGER_NAME MESSAGE`.
- Регистрируются все ключевые операции: регистрация, вход, покупка, продажа.


## Доступные команды CLI

### Основные операции

```bash
# Регистрация пользователя
register --username <username> --password <password>


# Вход в систему
login --username <username> --password <password>

# Просмотр портфеля (по умолчанию — в USD)
show-portfolio [--base <currency>]


# Покупка валюты
buy --currency <code> --amount <amount>

# Продажа валюты
sell --currency <code> --amount <amount>


# Получение курса между валютами
get-rate --from <currency> --to <currency>
```

### Работа с курсами

```bash
# Обновление всех курсов
update-rates


# Обновление только криптовалют (через CoinGecko)
update-rates --source coingecko


# Обновление только фиатных валют (через ExchangeRate API)
update-rates --source exchangerate


# Просмотр кэшированных курсов
show-rates [--currency <code>] [--top <N>] [--base <currency>]


# Список поддерживаемых валют
list-currencies
```

## Примеры использования

```bash
poetry run project
register --username alice --password secure123
login --username alice --password secure123
show-portfolio --base USD
list-currencies
show-rates --top 3
show-rates --currency BTC --base EUR
get-rate --from BTC --to USD
buy --currency BTC --amount 0.01
buy --currency EUR --amount 1000
show-portfolio
sell --currency BTC --amount 0.005
show-portfolio --base USD
exit
```

## Дополнительная информация

- Для просмотра записи сеанса работы см. [asciinema](https://asciinema.org/a/7BV0b36f1vhJgjVzRkgHcNMoO).
- Настройки приложения можно изменить в `infra/settings.py`.
- Для форматирования кода используйте `make lint`.