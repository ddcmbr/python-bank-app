import sqlite3


class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
        self.history = []

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.balance == other.balance and self.owner == other.owner
            

    def __add__(self, other):
        if isinstance(other, Account):
            return self.balance + other.balance
        elif isinstance(other, bool):
            raise TypeError(f'Нельзя вводить значения True/False')
        elif isinstance(other, (int, float)):
            return self.balance + other
        else:
            raise TypeError(f'Нельзя сложить Account и {type(other).__name__}')

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError('Число должно быть больше нуля!')
        self._balance += amount
        self.history.append(f'Пополнение счета "{self.owner}" +{amount} ₽.')

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError('Нужно вводить сумму больше нуля!')
        if amount > self.balance:
            raise ValueError('Недостаточно средств на балансе!')
        self._balance -= amount
        self.history.append(f'Снятие со счета "{self.owner}" на сумму: {amount} ₽.')
        print(f'  {self.owner}: {self.balance}₽ ({len(self.history)} операций)')

    def __str__(self):
        return f'{self.owner}: {self.balance}₽'

    def __repr__(self):
        return f'Account(owner = "{self.owner}", balance = {self.balance})'

class CreditAccount(Account):
    def __init__(self, owner, balance=0,credit_limit = 50000):
        super().__init__(owner, balance)
        self.credit_limit = credit_limit

    def withdraw(self,amount):
        if amount <=0:
            raise ValueError('Нельзя снять отрицательную сумму!')

        max_sum = self.balance + self.credit_limit
        if amount > max_sum:
            raise ValueError('Сумма для снятия превышает лимит!')

        self._balance -= amount

    def __repr__(self):
        return f'CreditAccount (owner = "{self.owner}", balance = {self.balance})'

class Bank:
    """
┌──────────────┐
│    Bank      │
│ ─────────── │
│ accounts: [] │  ← список
│              │
│ add_account  │
│ find_account │
│ show_all     │
│ total_money  │
└──────┬───────┘
       │ содержит
       ▼
┌──────────────┐
│   Account    │
│ ───────────  │
│ owner: ""    │
│ balance: 0   │
│ history: []  │
│              │
│ deposit      │
│ withdraw     │
│ transfer     │
└──────────────┘
"""
    def __init__(self, db_file='bank.db'):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
        id integer PRIMARY KEY AUTOINCREMENT,
        owner text NOT NULL,
        balance integer DEFAULT 0
        )
        """)

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER,
        record TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """)
        self.conn.commit()

    # --- Работа с базой данных и счетами ---
    def add_account(self, owner, balance=0):
        self.cursor.execute('INSERT INTO accounts (owner,balance) VALUES (?,?)',
        (owner, balance)
        )
        self.conn.commit()
        print('\nДАННЫЕ ОБНОВЛЕНЫ')
        print(f'Добавлен счет {owner}, с балансом {balance}₽')

    def find_account(self, owner):
        self.cursor.execute('SELECT * FROM accounts WHERE owner = ?',
        (owner,)
        )
        row = self.cursor.fetchone()

        if row:  # СЕЙЧАС ROW ЭТО КОРТЕЖ!
            id, owner, balance = row  # ЭТО НАЗЫВАЕТСЯ РАСПАКОВКА!
            return Account(owner, balance)
        return None

    def update_balance(self, owner, new_balance):
        self.cursor.execute(
            'UPDATE accounts SET BALANCE = ? WHERE owner = ?',
            (new_balance, owner)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def add_history(self, owner, record):
        self.cursor.execute('SELECT id FROM accounts WHERE owner = ?',
        (owner,)
        )
        row = self.cursor.fetchone()
        if row:
            account_id = row[0]
            self.cursor.execute('INSERT INTO history (account_id, record) VALUES(?,?)',
            (account_id, record)
            )
        self.conn.commit()

    # --- Операции банка ---
    def get_history(self,owner):
        acc = self.find_account(owner)
        if not acc:
            raise ValueError('Такого счета нет!')
        self.cursor.execute('SELECT id FROM accounts WHERE owner = ?',
                            (owner,)
                            )
        idrow = self.cursor.fetchone()
        id = idrow[0]
        self.cursor.execute('SELECT record FROM history WHERE account_id = ?',
                            (id,)
                            )
        rows = self.cursor.fetchall()
        records = []
        for row in rows:
            records.append(row[0])
        return records
    def account_check(self, name):
        acc = self.find_account(name)
        if not acc:
            raise ValueError('Счет не найден!')

    def withdraw(self, owner, amount):
        acc = self.find_account(owner)
        if not acc:
            raise ValueError('Счет не найден!')
        acc.withdraw(amount)
        self.update_balance(owner, acc.balance)
        self.add_history(owner, f'Снятие со счета {owner}, на сумму -{amount}₽')
        return acc.balance

    def deposit(self,owner,amount):
        acc = self.find_account(owner)
        if not acc:
            raise ValueError('Счет не найден')
        acc.deposit(amount)
        self.update_balance(owner,acc.balance)
        self.add_history(owner,f'Пополнение счета "{owner}" +{amount} ₽.' )
        return acc.balance

    def transfer(self,sender,receiver,amount):
        sender_acc = self.find_account(sender)
        receiver_acc = self.find_account(receiver)

        if not sender_acc:
            raise ValueError('Счет отправителя не найден!')
        if not receiver_acc:
            raise ValueError('Счет получателя не найден!')
        if sender == receiver:
            raise ValueError('Вы не можете соверишить перевод самому себе!')

        sender_acc.withdraw(amount)
        self.add_history(sender, f'Перевод на счет {receiver}: -{amount}₽')
        receiver_acc.deposit(amount)
        self.add_history(receiver,f'Перевод со счета {sender}:+{amount}₽')
        self.update_balance(sender, sender_acc.balance)
        self.update_balance(receiver, receiver_acc.balance)
    
    # --- Просмотр и статистика ---
    def show_all(self):
        self.cursor.execute('SELECT * FROM accounts')
        rows = self.cursor.fetchall()

        if not rows:
            print('\nСПИСОК АККАУНТОВ ПУСТ!')
            return

        print('═══════════════════════════════════')
        print('           БАНК')
        print('═══════════════════════════════════')
        for row in rows:
            id, owner, balance = row
            print(f' {owner}: {balance}₽')
        print('═══════════════════════════════════')

    def show_history(self, owner):
        self.cursor.execute('SELECT id FROM accounts where owner = ?',
        (owner,)
        )
        row = self.cursor.fetchone()

        if not row:
            print('Счет не найден!')
            return None

        id = row[0]
        self.cursor.execute('SELECT record FROM history WHERE account_id = ?',
        (id,)
        )
        history_rows = self.cursor.fetchall()

        if not history_rows:
            print('История пуста! ')
            return None

        print(f'=== ИСТОРИЯ ОПЕРАЦИЙ ({owner}) ===')
        for x in history_rows:
            print(x[0])
        print('='*35)

    def total_money(self):
        self.cursor.execute('SELECT SUM(balance) FROM accounts')
        result = self.cursor.fetchone()  # TOTAL ЭТО ОПЯТЬ КОРТЕЖ, МЫ ИЗВЛЕКАЕМ ИЗ НЕГО ПЕРВОЕ ЗНАЧЕНИЕ ПО ИНДЕКСУ
        total = result[0]
        if total is None:
            total = 0
        return total
        
    def _user_balance(self,owner):
        self.cursor.execute('SELECT balance FROM accounts WHERE owner = ?',
         (owner,)
         )
        row = self.cursor.fetchone()
        balance = row[0]
        return balance

# --- Пользовательский интерфейс (Консольное меню) ---
if __name__ == '__main__':
    menu = """
1. Создать счет
2. Показать все счета
3. Пополнить счет
4. Снять со счета
5. Перевести деньги
6. Показать историю операций
7. Показать общую сумму
8. Выход
"""
    bank = Bank()
    user_choice = 0

    print(menu)
    while True:
        confirmation = 0
        try:
            user_choice = int(input('Введите номер пункта меню: '))
        except ValueError:
            print('Нужно ввести число!')
            continue

        if user_choice == 1:
            name = input('Введите имя владельца счета: ').strip()
            try:
                balance = int(input('Введите баланс счета: '))
                bank.add_account(name, balance)
            except ValueError:
                print('Нужно ввести число!')
                continue
            print(f'\nСчет на имя {name}, с балансом {balance}₽ успешно добавлен!')
        elif user_choice == 2:
            bank.show_all()

        elif user_choice == 3:
            name = input('Введите имя владельца счета: ').strip()

            try:
                amount = int(input('Введите сумму для пополнения: '))   
                new_balance = bank.deposit(name, amount)

            except ValueError as e:
                print(f'Ошибка: {e}')
                continue

            print(f'\nСчет пополнен! Новый баланс: {new_balance}₽')

        elif user_choice == 4:
            name = input('Введите имя владельца счета: ').strip()

            try:
                amount = int(input('Введите сумму для снятия: '))
                bank.withdraw(name, amount)
                print(f'Успешно снято {amount} ₽ со счета {name}!')
                continue
            except ValueError as e:
                print(f'Ошибка!: {e}')
                continue

        elif user_choice == 5:

            try:
                sender = input('Введите имя отправителя: ').strip()
                receiver = input('Введите имя получателя: ').strip()
                transfer_amount = int(input('Введите сумму для перевода: '))

                bank.transfer(sender,receiver,transfer_amount)
                print(f'\nУспешный перевод со счета {sender}, на сумму: {transfer_amount}₽. На счет {receiver}.')

            except ValueError as e:
                print(f'Ошибка: {e}')
                continue
        
        elif user_choice == 6:
            name = input('Введите имя владельца счета для просмотра истории: ')
            bank.show_history(name)

        elif user_choice == 7:
            print(f'Общая сумма : {bank.total_money()}₽')

        elif user_choice == 8:
            print('Выйти? Да\\нет')
            confirmation = input('').strip().lower()
            if confirmation == 'да':
                break
            else:
                continue

        else:
            print('Такого пункта нет!')