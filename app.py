import tkinter as tk
from tkinter import messagebox
from bankwithsqlite import Bank

def show_balance_on_click():

    username = name_entry.get()
    if not username:
        messagebox.showerror('Ошибка', 'Вы забыли ввести имя!')
        return
    
    acc = bank.find_account(username)
    if acc:
        messagebox.showinfo('Баланс', f'Баланс клиента, {username}: {acc.balance}₽')
        name_entry.delete(0, tk.END)
        return
    else:
        messagebox.showerror('Ошибка', 'Счет с таким именем не найден!')
        return

def deposit_on_click():
    username = name_entry.get()
    try:
        amount = int(summ_operation_entry.get())
        new_balance = bank.deposit(username,amount)
        messagebox.showinfo(f'Счет успешно пополнен', f'Новый баланс: {new_balance}₽')
        name_entry.delete(0, tk.END)
        summ_operation_entry.delete(0,tk.END)
    except ValueError as e:
        messagebox.showerror('Ошибка', f'{e}')

def withdraw_on_click():
    username = name_entry.get()
    try:
        amount = int(summ_operation_entry.get())
        new_balance = bank.withdraw(username,amount)
        messagebox.showinfo(f'Успешно снято', f'Снято со счета: -{amount}₽\nНовый баланс {new_balance}₽')
        name_entry.delete(0, tk.END)
        summ_operation_entry.delete(0,tk.END)
    except ValueError as e:
        messagebox.showerror('Ошибка', f'{e}')

def create_account_on_click():
    username = name_entry.get()
    if not username:
        messagebox.showerror('Ошибка', 'Вы забыли ввести имя!')
        return
    amount = summ_operation_entry.get()
    if not amount:
        amount = 0
    else:
        try:
            amount = int(summ_operation_entry.get())
        except ValueError as e:
            messagebox.showerror('Ошибка!', 'Нужно ввести число!')
            return

    acc = bank.find_account(username)
    if acc:
        messagebox.showerror('Ошибка', 'Такой счет уже существует!')
        return
    try:
        bank.add_account(username,amount)
        messagebox.showinfo(f'Счет успешно создан', f'Счет для {username} успешно создан!')
        name_entry.delete(0, tk.END)
        summ_operation_entry.delete(0,tk.END)
    except ValueError as e:
        messagebox.showerror('Ошибка', f'{e}')

def history_on_click():

    username = name_entry.get()
    if not username:
        messagebox.showerror('Ошибка', 'Вы забыли ввести имя!')
        return
    try:
        history_list = bank.get_history(username)
        if not history_list:
            messagebox.showinfo('','У клиента пока нет операций')
            return
        messagebox.showinfo('История', f'{"\n".join(history_list)}')

    except ValueError as e:
        messagebox.showerror('Ошибка', f'{e}')

def open_transfer():
    def transfer():
        sender = sender_name_entry.get()
        if not sender:
            messagebox.showerror('Ошибка', f'Отправитель не найден!')
            return
        receiver = receiver_name_entry.get()
        if not receiver:
            messagebox.showerror('Ошибка','Получатель не найден!')
            return
        amount = transfersumentry.get()
        if not amount:
            messagebox.showerror('Ошибка', 'Вы ничего не ввели!')
            return
        try:
            amount = int(transfersumentry.get())
            bank.transfer(sender,receiver,amount)
            messagebox.showinfo('Успешно', f'Успешный перевод со счета {sender} на счет {receiver}\nПеревод на сумму {amount}₽')
        except ValueError as e:
            messagebox.showerror('Ошибка',f'{e}')
    def close_open_transfer():
        transfer_window.destroy()

    transfer_window = tk.Toplevel(window)
    transfer_window.title('Перевод денег')
    transfer_window.geometry('400x300')
    sender_name_label = tk.Label(transfer_window, text = 'Отправитель', font = ('arial', 13))
    sender_name_label.pack(pady=10)
    sender_name_entry = tk.Entry(transfer_window, font =('arial',12))
    sender_name_entry.pack(pady = 9)
    receiver_name_label = tk.Label(transfer_window, text = 'Получатель', font = ('arial', 13))
    receiver_name_label.pack(pady = 8)
    receiver_name_entry = tk.Entry(transfer_window, font = ('arial', 12))
    receiver_name_entry.pack(pady=7)
    transfersum = tk.Label(transfer_window, text = 'Введите сумму для перевода', font = ('arial', 13))
    transfersum.pack(pady=6)
    transfersumentry = tk.Entry(transfer_window, font = ('arial', 12))
    transfersumentry.pack(pady=5)
    transfer_btn = tk.Button(transfer_window,text = 'Перевод', command =transfer)
    transfer_btn.pack(side = tk.LEFT, padx =5)



# НАДПИСИ И ПОЛЯ ВВОДА
window = tk.Tk()
bank = Bank()
window.title('Банк')
window.geometry("480x400")


title_label = tk.Label(window, text = 'Добро пожаловать в Банк!', font=('Arial', 14))
title_label.pack(pady=10)

name_label = tk.Label(window, text = f'Имя клиента:', font =('Arial',13))
name_label.pack(pady = 9)
name_entry = tk.Entry(window, font=("Arial", 12))
name_entry.pack(pady=8)

summ_operation = tk.Label(window, text = 'Сумма операции(₽)', font = ('Arial', 13))
summ_operation.pack(pady = 7)
summ_operation_entry = tk.Entry(window, font = ('arial', 12))
summ_operation_entry.pack(pady = 6)

# КНОПКИ
btn_frame = tk.Frame(window)
btn_frame.pack(pady=15)
history_btn = tk.Button(btn_frame, text = 'История', command = history_on_click)
history_btn.pack(side = tk.LEFT, padx = 5)
create_account_btn = tk.Button(btn_frame, text = 'Создать счет', command = create_account_on_click)
create_account_btn.pack(side = tk.LEFT, padx= 5)
show_balance_btn = tk.Button(btn_frame, text='Узнать баланс', command = show_balance_on_click)
show_balance_btn.pack(side = tk.LEFT,padx=5)
summ_operation_deposit_btn = tk.Button(btn_frame, text = 'Пополнить', command = deposit_on_click)
summ_operation_deposit_btn.pack(side = tk.LEFT,padx=5)
summ_operation_withdraw_btn = tk.Button(btn_frame, text = 'Снять', command = withdraw_on_click)
summ_operation_withdraw_btn.pack(side = tk.LEFT,padx = 5)
open_transfer_btn = tk.Button(btn_frame, text ='Перевод',command = open_transfer)
open_transfer_btn.pack(side=tk.LEFT, padx = 5)
window.mainloop()