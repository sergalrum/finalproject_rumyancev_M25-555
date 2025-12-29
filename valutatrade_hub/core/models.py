import hashlib
import json
from datetime import datetime
from typing import Dict, Any



class User:
    def __init__(self, user_id: int, username: str, password: str):
        if not username:
            raise ValueError("Имя пользователя не может быть пустым.")
        if len(password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов.")

        self._user_id = user_id
        self._username = username
        self._salt = self._generate_salt()
        self._hashed_password = self._hash_password(password)
        self._registration_date = datetime.utcnow()

    def _generate_salt(self) -> str:
        """Генерирует случайную соль."""
        return hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:8]

    def _hash_password(self, password: str) -> str:
        """Хеширует пароль с солью."""
        return hashlib.sha256((password + self._salt).encode()).hexdigest()

    def get_user_info(self) -> Dict[str, Any]:
        """Возвращает информацию о пользователе без пароля."""
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat()
        }

    def change_password(self, new_password: str):
        """Изменяет пароль пользователя."""
        if len(new_password) < 4:
            raise ValueError("Новый пароль должен быть не короче 4 символов.")
        self._salt = self._generate_salt()
        self._hashed_password = self._hash_password(new_password)

    def verify_password(self, password: str) -> bool:
        """Проверяет введённый пароль."""
        return self._hash_password(password) == self._hashed_password

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username


class Wallet:
    def __init__(self, currency_code: str, initial_balance: float = 0.0):
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым.")
        if initial_balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным.")

        self.currency_code = currency_code
        self._balance = initial_balance

    @property
    def balance(self) -> float:
        return self._balance

    @balance.setter
    def balance(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс должен быть числом.")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным.")
        self._balance = float(value)

    def deposit(self, amount: float):
        """Пополняет баланс."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительным числом.")
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        """Снимает средства, если баланс позволяет."""
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Сумма снятия должна быть положительным числом.")
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

    def get_balance_info(self) -> Dict[str, Any]:
        """Возвращает информацию о балансе."""
        return {
            "currency_code": self.currency_code,
            "balance": self.balance
        }



class Portfolio:
    def __init__(self, user_id: int):
        self._user_id = user_id
        self._wallets: Dict[str, Wallet] = {}

    def add_currency(self, currency_code: str):
        """Добавляет новый кошелёк в портфель, если его ещё нет."""
        if not currency_code:
            raise ValueError("Код валюты не может быть пустым.")
        if currency_code in self._wallets:
            raise ValueError(f"Валюта {currency_code} уже есть в портфеле.")
        self._wallets[currency_code] = Wallet(currency_code)

    def get_total_value(self, base_currency: str = 'USD') -> float:
        """
        Возвращает общую стоимость всех валют в базовой валюте.
        Для упрощения используем фиктивные курсы.
        """
        exchange_rates = {
            'USD': 1.0,
            'EUR': 1.1,
            'BTC': 50000.0,
            # Добавьте другие валюты по необходимости
        }
        total = 0.0
        for wallet in self._wallets.values():
            rate = exchange_rates.get(wallet.currency_code, 1.0)
            total += wallet.balance * rate
        return total

    def get_wallet(self, currency_code: str) -> Wallet:
        """Возвращает кошелёк по коду валюты."""
        if currency_code not in self._wallets:
            raise KeyError(f"Валюта {currency_code} не найдена в портфеле.")
        return self._wallets[currency_code]

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def wallets(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает копию словаря кошельков в формате для JSON."""
        return {code: wallet.get_balance_info() for code, wallet in self._wallets.items()}
