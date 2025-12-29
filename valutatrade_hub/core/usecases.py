from .models import User, Portfolio, Wallet
from .utils import load_json, save_json

def register_user(username: str, password: str) -> dict:
    users = load_json("users.json")
    if username in [u["username"] for u in users.values()]:
        raise ValueError(f"Имя пользователя '{username}' уже занято")
    
    user_id = max(users.keys(), default=0) + 1
    user = User(user_id, username, password)
    users[user_id] = user.get_user_info()
    save_json("users.json", users)
    
    # Создаём пустой портфель
    portfolios = load_json("portfolios.json")
    portfolios[user_id] = {"user_id": user_id, "wallets": {}}
    save_json("portfolios.json", portfolios)
    
    return {"user_id": user_id, "username": username}

def login_user(username: str, password: str) -> User:
    users_data = load_json("users.json")
    for user_id, data in users_data.items():
        if data["username"] == username:
            user = User(user_id, username, password)  # Временный объект для проверки
            if user.verify_password(password):
                return user
            else:
                raise ValueError("Неверный пароль")
    raise ValueError(f"Пользователь '{username}' не найден")

def get_portfolio(user_id: int, base_currency: str = "USD") -> dict:
    portfolios = load_json("portfolios.json")
    if user_id not in portfolios:
        return {"user_id": user_id, "wallets": {}, "total_value": 0.0}
    
    portfolio_data = portfolios[user_id]
    portfolio = Portfolio(user_id)
    for code, balance in portfolio_data["wallets"].items():
        wallet = Wallet(code, balance)
        portfolio._wallets[code] = wallet
    
    total = portfolio.get_total_value(base_currency)
    return {
        "user_id": user_id,
        "wallets": portfolio.wallets,
        "total_value": total,
        "base_currency": base_currency
    }

def buy_currency(user_id: int, currency: str, amount: float) -> dict:
    # Заглушка: просто добавляем валюту в портфель
    portfolios = load_json("portfolios.json")
    if user_id not in portfolios:
        raise ValueError("Портфель не найден")
    
    if currency not in portfolios[user_id]["wallets"]:
        portfolios[user_id]["wallets"][currency] = 0.0
    
    portfolios[user_id]["wallets"][currency] += amount
    save_json("portfolios.json", portfolios)
    
    return {
        "currency": currency,
        "amount": amount,
        "rate": 1.0,  # Заглушка курса
        "cost_usd": amount * 1.0
    }

def sell_currency(user_id: int, currency: str, amount: float) -> dict:
    portfolios = load_json("portfolios.json")
    if user_id not in portfolios:
        raise ValueError("Портфель не найден")
    if currency not in portfolios[user_id]["wallets"]:
        raise ValueError(f"У вас нет кошелька '{currency}'")
    if portfolios[user_id]["wallets"][currency] < amount:
        available = portfolios[user_id]["wallets"][currency]
        raise ValueError(f"Недостаточно средств: доступно {available}, требуется {amount}")
    
    portfolios[user_id]["wallets"][currency] -= amount
    save_json("portfolios.json", portfolios)
    
    return {
        "currency": currency,
        "amount": amount,
        "rate": 1.0,
        "revenue_usd": amount * 1.0
    }

def get_rate(from_currency: str, to_currency: str) -> dict:
    rates = load_json("rates.json")
    key = f"{from_currency}_{to_currency}"
    if key in rates:
        return {
            "rate": rates[key]["rate"],
            "updated_at": rates[key]["updated_at"]
        }
    # Заглушка
    return {"rate": 1.0, "updated_at": "2025-12-29T14:30:00"}
