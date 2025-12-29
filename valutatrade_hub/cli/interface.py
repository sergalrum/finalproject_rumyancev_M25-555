import sys
import json
import shlex
from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from valutatrade_hub.core.usecases import (
    register_user, login_user, get_portfolio, buy_currency, sell_currency, get_rate
)


class CLI:
    def __init__(self):
        self.current_user = None  # Для хранения залогиненного пользователя
        self.parser = self._create_parser()

    def _create_parser(self) -> ArgumentParser:
        """Создаёт парсер аргументов для всех команд."""
        parser = ArgumentParser(
            description="ValutaTrade Hub CLI",
            formatter_class=RawDescriptionHelpFormatter
        )
        subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

        # register
        register_parser = subparsers.add_parser("register", help="Зарегистрировать пользователя")
        register_parser.add_argument("--username", type=str, required=True)
        register_parser.add_argument("--password", type=str, required=True)

        # login
        login_parser = subparsers.add_parser("login", help="Войти в систему")
        login_parser.add_argument("--username", type=str, required=True)
        login_parser.add_argument("--password", type=str, required=True)

        # show-portfolio
        show_parser = subparsers.add_parser("show-portfolio", help="Показать портфель")
        show_parser.add_argument("--base", type=str, default="USD")

        # buy
        buy_parser = subparsers.add_parser("buy", help="Купить валюту")
        buy_parser.add_argument("--currency", type=str, required=True)
        buy_parser.add_argument("--amount", type=float, required=True)

        # sell
        sell_parser = subparsers.add_parser("sell", help="Продать валюту")
        sell_parser.add_argument("--currency", type=str, required=True)
        sell_parser.add_argument("--amount", type=float, required=True)

        # get-rate
        rate_parser = subparsers.add_parser("get-rate", help="Получить курс")
        rate_parser.add_argument("--from", type=str, required=True, dest="from_currency")
        rate_parser.add_argument("--to", type=str, required=True, dest="to_currency")


        return parser

    def _parse_input(self, input_str: str) -> ArgumentParser.parse_args:
        """Парсит строку ввода в аргументы."""
        try:
            args = shlex.split(input_str)
            return self.parser.parse_args(args)
        except SystemExit:
            raise ValueError("Некорректный ввод. Используйте 'help' для списка команд.")

    def _print_help(self):
        """Выводит справку по командам."""
        print("\n" + "="*50)
        print("VALUTATRADE HUB CLI — Помощь")
        print("="*50)
        print("Доступные команды:")
        print("  register --username <имя> --password <пароль>  - Регистрация нового пользователя")
        print("  login --username <имя> --password <пароль>     - Вход в систему")
        print("  show-portfolio [--base <валюта>]               - Показать портфель (база USD)")
        print("  buy --currency <код> --amount <сумма>          - Купить валюту")
        print("  sell --currency <код> --amount <сумма>         - Продать валюту")
        print("  get-rate --from <код> --to <код>             - Получить курс валют")
        print("  help                                            - Показать эту справку")
        print("  exit                                            - Выход из системы")
        print("="*50 + "\n")

    def _execute_command(self, args):
        """Выполняет команду на основе аргументов."""
        if args.command == "register":
            try:
                result = register_user(args.username, args.password)
                print(f"\n✅ Пользователь '{result['username']}' зарегистрирован (id={result['user_id']}).")
                print("Войдите: login --username {result['username']} --password ****\n")
            except ValueError as e:
                print(f"\n❌ Ошибка регистрации: {e}\n")


        elif args.command == "login":
            try:
                self.current_user = login_user(args.username, args.password)
                print(f"\n✅ Вы вошли как '{self.current_user.username}'\n")
            except ValueError as e:
                print(f"\n❌ Ошибка входа: {e}\n")

        elif args.command == "show-portfolio":
            if not self.current_user:
                print("\n❌ Сначала выполните login\n")
                return
            try:
                portfolio = get_portfolio(self.current_user.user_id, args.base)
                print(f"\n📊 Портфель пользователя '{self.current_user.username}' (база: {portfolio['base_currency']}):")
                if not portfolio["wallets"]:
                    print("  • Портфель пуст")
                else:
                    for code, balance in portfolio["wallets"].items():
                        value_usd = balance["balance"] * 1.0  # Заглушка расчёта
                        print(f"!  • {code}: {balance['balance']:.4f} → {value_usd:.2f} {portfolio['base_currency']}")
                print(f"!  {'─'*40}")
                print(f"!  Итого: {portfolio['total_value']:.2f} {portfolio['base_currency']}\n")
            except Exception as e:
                print(f"\n❌ Ошибка при загрузке портфеля: {e}\n")

        elif args.command == "buy":
            if not self.current_user:
                print("\n❌ Сначала выполните login\n")
                return
            if args.amount <= 0:
                print("\n❌ 'amount' должен быть положительным числом\n")
                return
            try:
                result = buy_currency(self.current_user.user_id, args.currency.upper(), args.amount)
                print(f"\n✅ Покупка выполнена: {result['amount']:.4f} {result['currency']}")
                print(f"!   Курс: {result['rate']:.2f} USD/{result['currency']}")
                print(f"!   Стоимость: {result['cost_usd']:.2f} USD")
                print("\nИзменения в портфеле:")
                print(f"!  • {result['currency']}: было ? → стало {result['amount']:.4f}\n")
            except ValueError as e:
                print(f"\n❌ Ошибка покупки: {e}\n")

        elif args.command == "sell":
            if not self.current_user:
                print("\n❌ Сначала выполните login\n")
                return
            if args.amount <= 0:
                print("\n❌ 'amount' должен быть положительным числом\n")
                return
            try:
                result = sell_currency(self.current_user.user_id, args.currency.upper(), args.amount)
                print(f"\n✅ Продажа выполнена: {result['amount']:.4f} {result['currency']}")
                print(f"!   Курс: {result['rate']:.2f} USD/{result['currency']}")
                print(f"!   Выручка: {result['revenue_usd']:.2f} USD")
                print("\nИзменения в портфеле:")
                print(f"!  • {result['currency']}: было ? → стало ?\n")
            except ValueError as e:
                print(f"\n❌ Ошибка продажи: {e}\n")

        elif args.command == "get-rate":
            try:
                rate_info = get_rate(args.from_currency.upper(), args.to_currency.upper())
                print(f"\n💹 Курс {args.from_currency}→{args.to_currency}: {rate_info['rate']:.6f}")
                print(f"!   Обновлено: {rate_info['updated_at']}")
                reverse_rate = 1 / rate_info['rate'] if rate_info['rate'] != 0 else 0
                print(f"!   Обратный курс {args.to_currency}→{args.from_currency}: {reverse_rate:.6f}\n")
            except Exception as e:
                print(f"\n❌ Ошибка получения курса: {e}\n")

        elif args.command == "help":
            self._print_help()

        else:
            print(f"\n❌ Неизвестная команда: {args.command}. Используйте 'help' для списка команд.\n")

    def run(self):
        """Запускает интерактивный CLI."""
        print("🚀 ValutaTrade Hub CLI запущен. Введите 'help' для списка команд.")
        
        while True:
            try:
                # Читаем ввод пользователя
                user_input = input("\n> ").strip()
                
                # Пропускаем пустые строки
                if not user_input:
                    continue
                
                # Обрабатываем специальные команды
                if user_input.lower() == "exit":
                    print("\n👋 До свидания!\n")
                    break
                elif user_input.lower() == "help":
                    self._print_help()
                    continue
                
                # Парсим и выполняем команду
                args = self._parse_input(user_input)
                self._execute_command(args)

            except KeyboardInterrupt:
                print("\n\n👋 Прервано пользователем. До свидания!\n")
                break
            except EOFError:
                print("\n\n👋 Конец ввода. До свидания!\n")
                break
            except Exception as e:
                print(f"\n❌ Неожиданная ошибка: {type(e).__name__}: {e}\n")
