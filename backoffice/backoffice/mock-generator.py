import psycopg2
import random
from time import perf_counter
import multiprocessing 



transactions = [
    {'amount':1,'description':'Icecream'},
    {'amount':0.5,'description':'Water'},
    {'amount':2,'description':'Chips'},
    {'amount':2.5,'description':'Sandwich'},
]




# start = perf_counter()
# for i in range(n):
#     seller = random.randint(1, n)
#     buyer = random.randint(1, n)
#     if seller == buyer:
#         continue
#     amount, description = random.choice(transactions).values()
#     print(amount, description)
#     cur.execute('INSERT INTO transactions(seller_id, amount, description, transaction_type_id, transaction_status_id) VALUES (%s, %s, %s, 3, 1) RETURNING transactions.id;', (seller, amount, description) )
#     transaction_id = cur.fetchone()[0]
#     conn.commit()

#     print(transaction_id)
#     cur.execute('UPDATE transactions SET buyer_id = %s WHERE id = %s', (buyer, transaction_id,) )
# end = perf_counter()
# print(end-start)



def runQuery(query): 
    conn = psycopg2.connect("dbname=qrpayment user=simo")
    cur = conn.cursor()
    cur.execute(query) 
    conn.commit() 
    conn.close()

def gen_data():
    n = 137000
    k = 50000
    queries = []
    for i in range(n+1):
        year = 2020
        month = random.randint(1,12)
        day = random.randint(1, 28)
        hour = random.randint(0,23)
        minute = random.randint(0,58)
        second = random.randint(0,59)


        timestamp = f'{year}-{month}-{day} {hour}:{minute}:{second}'
        timestamp2 = f'{year}-{month}-{day} {hour}:{minute+1}:{second}'

        # Administrative transaction query
        #query = f"INSERT INTO transactions(seller_id, amount, description, transaction_type_id, transaction_status_id, creation_time, status_update_time) VALUES ({i+1}, 200, 'Deposit into account', 2, 2, '{timestamp}', '{timestamp2}');"
        
        seller = random.randint(1, k)
        buyer = random.randint(1, k)
        if seller == buyer:
            continue

        amount, description = random.choice(transactions).values()
        query = f"INSERT INTO transactions(seller_id, buyer_id, amount, description, transaction_type_id, transaction_status_id, creation_time, status_update_time) VALUES ({seller}, {buyer}, {amount}, '{description}', 3, 1, '{timestamp}', '{timestamp2}');"
        
        queries.append(query)  
    return queries


if __name__ == "__main__":
    pool = multiprocessing.Pool(25)
    queries = gen_data()
    start = perf_counter()
    for i in pool.imap_unordered(runQuery, queries, 1370):
        continue
    end = perf_counter()
    print(end-start)