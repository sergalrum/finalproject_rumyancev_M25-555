# ValutaTrade Hub

**Платформа для отслеживания и симуляции торговли валютами** (учебный финальный проект). Реализована как Python‑пакет с консольным интерфейсом (CLI).

## Стек и инструменты

- **Python 3.12+** — язык реализации;
- **Poetry** — управление зависимостями и сборкой;
- **Ruff** — линтер и форматтер (соответствие PEP8);
- **PrettyTable** — форматированный вывод таблиц в CLI;
- **Requests** — HTTP‑клиент для работы с внешними API;
- **python‑dotenv** — загрузка переменных окружения из `.env`;
- **Makefile** — унифицированный интерфейс запуска (install, project, build, lint).

## Быстрый старт

> Требуется установленный Poetry. На Windows удобно через `pipx`:  
> ```bash
> pipx install poetry
> ```

1. Установите зависимости:
   ```bash
   make install
   ```

2. Запустите CLI:
   ```bash
   make project
   ```

3. Соберите пакет:
   ```bash
   make build
   ```

4. Проверьте код линтером:
   ```bash
   make lint
   ```

**Примечание для Windows**:  
- Используйте Git Bash или совместимую реализацию `make`.  
- Если `make` недоступен, применяйте прямые команды Poetry:  
  ```bash
  poetry run project
  ```

## Доступные команды CLI

### Основные операции
- `register` — регистрация пользователя;
- `login` — вход (создаёт локальную сессию);
- `show-portfolio` — показать портфель в базовой валюте (по умолчанию USD);
- `buy` — купить валюту (списывает USD);
- `sell` — продать валюту (зачисляет USD);
- `deposit` — пополнить кошелёк (по умолчанию USD);
- `withdraw` — снять средства (по умолчанию USD).


### Работа с курсами
- `get-rate` — получить курс пары (с локальным кешем);
- `list-currencies` — список поддерживаемых валют;
- `update-rates` — обновить курсы из внешних API (Parser Service):  
  - `--source exchangerate|coingecko` — источник данных;  
  - `--strict` — жёсткая замена снимка без слияний;  
  - `--all-fiat` — все фиатные валюты (иначе только EUR/GBP/RUB);  
  - `--no-history` — не писать в `exchange_rates.json` для этого запуска.
- `schedule` — периодическое обновление (цикл до `Ctrl+C`):  
  - `--interval 300` — интервал в секундах;  
  - остальные флаги аналогичны `update-rates`.
- `show-rates` — показать актуальные курсы из локального кеша:  
  - `--currency BTC` — фильтрация по валюте;  
  - `--top 2` — ограничение числа записей;  
  - `--base USD` — пересчёт в базовую валюту.
- `clear-history` — очистить `data/exchange_rates.json`.


### Примеры запуска (через `make`)
```bash
make project -- register --username alice --password 1234
make project -- login --username alice --password 1234
make project -- deposit --amount 1000
make project -- show-portfolio
make project -- buy --currency EUR --amount 10
make project -- get-rate --from EUR --to USD
make project -- list-currencies
```

## REPL‑режим

При запуске CLI без аргументов открывается интерактивный REPL. Введите `help` для списка команд.

**Примеры в REPL**:
```
login --username alice --password 1234
update-rates --strict --no-history
show-rates --base EUR --currency BTC
schedule --interval 600 --strict
```

## Обработка ошибок и сообщения

Пользователь получает понятные сообщения об ошибках:
- `InsufficientFundsError` → «Недостаточно средств: доступно X CODE, требуется Y CODE»;
- `CurrencyNotFoundError` → «Неизвестная валюта 'XXX'» (с подсказкой проверить код);
- `ApiRequestError` → «Ошибка при обращении к внешнему API: причина» (с рекомендацией повторить позже).


## Логирование

- Настраивается в `valutatrade_hub/logging_config.py` (вращающиеся файлы + вывод в консоль).
- Декоратор `@log_action` применяется к операциям `BUY/SELL`, `REGISTER/LOGIN`.
- В лог записываются:  
  - timestamp;  
  - действие;  
  - `user_id`/`username` (если доступны);  
  - валюта/сумма/курс (если применимо);  
  - результат (`OK`/`ERROR`).


## Кеширование курсов

- Курсы сохраняются в `data/rates.json` с TTL (по умолчанию 300 сек).  
- TTL настраивается в `pyproject.toml` (`[tool.valutatrade]`, ключ `rates_ttl_seconds`).  
- При истечении TTL автоматически запускается обновление через Parser Service.  
- **Автообновление при запуске**: если `last_refresh` в `data/rates.json` относится к прошлому дню, выполняется одноразовое обновление.  
- Отключение: переменная окружения `PARSER_AUTO_UPDATE_ON_START=0`.


## Parser Service: обновление и история

### Файлы данных
- **История измерений**: `data/exchange_rates.json`  
  - Каждая запись содержит: `id` (формат `FROM_TO_YYYY-MM-DDTHH:MM:SSZ`), `rate`, `timestamp` (UTC, ISO), `source`, `meta`.  
  - Дубликаты по `id` не добавляются.  
- **Снимок (быстрый кеш)**: `data/rates.json`  
  - Формат: `{ "pairs": { "EUR_USD": { "rate", "updated_at", "source" } }, "last_refresh": "..." }`.  
  - Сохраняются обе стороны пары (`EUR_USD` и `USD_EUR`).

### Режимы работы
- **Обычный режим**: «слияние по свежести» (более новые значения перекрывают старые).  
- **Строгий режим** (`--strict` или `PARSER_SNAPSHOT_STRICT=1`): полная замена снимка.  
- **Отключение истории** (`--no-history` или `PARSER_HISTORY_DISABLED=1`).

### Переменные окружения (`.env`)
- Приоритет: реальные переменные > значения из `.env`.  
- **Фиат (ExchangeRate‑API)**:  
  - Вариант A: `EXCHANGERATE_API_URL=https://v6.exchangerate-api.com/v6/<KEY>/latest/USD`.  
  - Вариант B: `EXCHANGERATE_API_KEY=<KEY>` (опционально `EXCHANGERATE_BASE=USD`).  
- **Крипто (CoinGecko)**: ключ не требуется для `simple/price`.  
  - Вариант A: `COINGECKO_FULL_URL=https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd`.  
  - Вариант B: `COINGECKO_URL=https://api.coingecko.com/api/v3/simple/price` (ids из `CRYPTO_ID_MAP`).  
- **Таймаут HTTP**: `PARSER_HTTP_TIMEOUT=10`.

## Иерархия валют

- Реализована в `valutatrade_hub/core/currencies.py`.  
- Поддерживаемые коды: USD, EUR, GBP, RUB, BTC, ETH, SOL.  
- Команда `list-currencies` выводит таблицу:

  ```
Fiat currencies:
  [FIAT] USD — US Dollar (Issuing: United States)
  [FIAT] EUR — Euro (Issuing: Eurozone)
  [FIAT] RUB — Russian Ruble (Issuing: Russia)
  [FIAT] GBP — British Pound (Issuing: United Kingdom)
  [FIAT] JPY — Japanese Yen (Issuing: Japan)

Cryptocurrencies:
  [CRYPTO] BTC — Bitcoin (Algo: SHA-256, MCAP: 1.12e+12)
  [CRYPTO] ETH — Ethereum (Algo: Ethash, MCAP: 4.50e+11)
  [CRYPTO] LTC — Litecoin (Algo: Scrypt, MCAP: 5.80e+09)
  [CRYPTO] ADA — Cardano (Algo: Ouroboros, MCAP: 1.20e+10)

  ```
