from bankwithsqlite import Account
from bankwithsqlite import CreditAccount

Zahar = Account('Zahar', 1000)

ZaharCredit = CreditAccount(Zahar.owner,1000)
ZaharCredit.withdraw(5000)
print(ZaharCredit.balance)
try:

    Zahar.withdraw(5000)
    print(Zahar.balance)
except ValueError as e:
    print('Ошибка!', f'{e}')

accounts = [Zahar, ZaharCredit]
print(accounts)

acc1 = Account('Иван', 5000)
acc2 = Account('Иван', 5000)
acc3 = Account('Иван', 1000)
print(acc1 == acc2)
print(acc1 == acc3)
print(acc1 == 'Иван')