# Write your code here
from collections import namedtuple
from random import randint
import sqlite3

BIN = "400000"
# last_account_id = 0
lenght_can = 16
check_sum = "0"
accounts = {}
Account = namedtuple('Account', ['account_id', 'pin', 'balance'])


def calculate_check_sum(new_acc):
    nacc = []
    for i, v in enumerate(new_acc):
        nc = int(v) * 2 if (i + 1) % 2 != 0 else int(v)
        nacc.append(nc)
    nacc = [x - 9 if x > 9 else x for x in nacc]
    if sum(nacc) % 10 == 0:
        return 0
    else:
        return 10 - sum(nacc) % 10


def get_last_account_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM card ORDER BY id DESC LIMIT 1;")
    r = cur.fetchone()
    if not r:
        return 0
    else:
        return r[0]


def add_new_account(conn, new_acc, pin):
    cur = conn.cursor()
    sql = f"INSERT INTO card (number, pin) VALUES ('{new_acc}', '{pin}');"
    cur.execute(sql)
    conn.commit()


def create_account(conn):
    last_account_id = get_last_account_id(conn)
    new_acc = BIN + '0' * (9 - len(str(last_account_id))) + str(last_account_id)
    new_acc = new_acc + str(calculate_check_sum(new_acc))
    pin = randint(0, 9999)
    pin = '0' * (4 - len(str(pin))) + str(pin)
    add_new_account(conn, new_acc, pin)

    print('Your card has been created')
    print('Your card number:')
    print(new_acc)
    print('Your card PIN:')
    print(pin)


def log_into_account(conn):
    command_info = None
    cur = conn.cursor()
    print('Enter your card number:')
    card_number = input()
    print('Enter your PIN:')
    pin = input()

    cur.execute(f"SELECT balance FROM card WHERE number = '{card_number}' AND pin = '{pin}';")
    r = cur.fetchone()

    if not r:
        print('Wrong card number or PIN!')
        command_info = 'wrong_pass'
    else:
        print('You have successfully logged in!')
        command_info = get_account_info(conn, card_number)
    return command_info


def validate_card(conn, from_card, to_card):

    if from_card == to_card:
        return "You can't transfer money to the same account!"

    sum_num = calculate_check_sum(to_card[:-1])
    if str(sum_num) != to_card[-1]:
        return 'Probably you made a mistake in the card number. Please try again!'

    cur = conn.cursor()
    cur.execute("SELECT * FROM card WHERE number = '{}'".format(to_card))
    r = cur.fetchone()
    if not r:
        return 'Such a card does not exist.'

def make_transfer(conn, from_card, to_card, amount):

    cur = conn.cursor()
    cur.execute(f"SELECT balance FROM card WHERE number = '{from_card}';")
    balance = cur.fetchone()[0]
    if balance < amount:
        return 'Not enough money!'
    else:
        cur.execute(f'UPDATE card SET balance = balance - {amount} WHERE number = {from_card};')
        cur.execute(f'UPDATE card SET balance = balance + {amount} WHERE number = {to_card};')
        conn.commit()
        return 'Success!'



def get_account_info(conn, card_num):
    cur = conn.cursor()
    while True:
        print(*['1. Balance', '2. Add Income', '3. Do transfer',
                '4. Close account', '5. Log out', '0. Exit'], sep='\n')
        task = input()
        if task == '1':
            cur.execute(f'SELECT balance FROM card WHERE number = {card_num};')
            balance = cur.fetchone()[0]
            print('Balance: {}'.format(balance))
        elif task == '2':
            print('Enter income:\n')
            income = input()
            sql = 'UPDATE card SET balance = balance +  {}  WHERE number = {};'.format(int(income), card_num)
            cur.execute(sql)
            conn.commit()
            print('Income was added!')
        elif task == '3':
            print('Transfer\n')
            print('Enter card number:\n')
            acc = input()
            r = validate_card(conn, card_num, acc)
            if r:
                print(r + '\n')
            else:
                print('Enter how much money you want to transfer:\n')
                amt = int(input())
                print(make_transfer(conn, card_num, acc, amt))

        elif task == '4':
            cur = conn.cursor()
            cur.execute(f"DELETE FROM card WHERE number = '{card_num}';")
            conn.commit()
            print('The account has been closed!')
            break

        elif task == '5':
            print('You have successfully logged out!')
            return 'log_out'
        elif task == '0':
            return 'exit'


conn = sqlite3.connect('./card.s3db')
create_table = "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT , pin TEXT, balance INTEGER DEFAULT 0);"
cur = conn.cursor()
cur.execute(create_table)
conn.commit()

while True:
    print(*['1. Create an account', '2. Log into account', '0. Exit'], sep='\n')
    task = input()
    if task == '1':
        create_account(conn)
    elif task == '2':
        command_info = log_into_account(conn)
        if command_info == 'exit':
            print('Bye!')
            break
    else:
        print('Bye!')
        break

conn.close()