import psycopg2
import random
from time import perf_counter

conn = psycopg2.connect("dbname=qrpayment user=simo")
cur = conn.cursor()

transactions = [
    {'amount':1,'description':'Icecream'},
    {'amount':0.5,'description':'Water'},
    {'amount':2,'description':'Chips'},
    {'amount':2.5,'description':'Sandwich'},
]

n = 50000

# start = perf_counter()
for i in range(n):
    seller = random.randint(1, n)
    buyer = random.randint(1, n)
    if seller == buyer:
        continue
    amount, description = random.choice(transactions).values()
    print(amount, description)
    cur.execute('INSERT INTO transactions(seller_id, amount, description, transaction_type_id, transaction_status_id) VALUES (%s, %s, %s, 3, 1) RETURNING transactions.id;', (seller, amount, description) )
    transaction_id = cur.fetchone()[0]
    conn.commit()

    print(transaction_id)
    cur.execute('UPDATE transactions SET buyer_id = %s WHERE id = %s', (buyer, transaction_id,) )
# end = perf_counter()
# print(end-start)



# start = perf_counter()
# for i in range(n):
    # cur.execute("INSERT INTO transactions(seller_id, amount, description, transaction_type_id, transaction_status_id) VALUES (%s, 249000, 'Deposit into account', 2, 2);", (i+1,))
# end = perf_counter()
# print(end-start)

conn.commit()
cur.close()
conn.close()


