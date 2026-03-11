"""
This file is used to test equivalent sql queries against our esql queries fed into our custom query processor. 
"""

import psycopg2
import psycopg2.extras
import tabulate
import sys

def query(num=None, print_output=True):
    if num is None:
        num = input("Query number(Give a number from 1 - 6): ")

    file = fr"inputs/sql_Query{num}.txt"
    with open(file, "r") as f:
        query = f.read()

    connection_params = {
        'dbname': 'YOUR_DBNAME',
        'host': 'YOUR_HOSTNAME',
        'port': '5432',
        'user': 'YOUR_USERNAME',
        'password': 'YOUR_PASSWORD'
    }

    conn = psycopg2.connect(**connection_params, cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute(query)
    result = tabulate.tabulate(cur.fetchall(), headers="keys", tablefmt="grid")
    
    if print_output:
        print(result)

    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query(sys.argv[1], print_output=False)
    else:
        query(print_output=True)


