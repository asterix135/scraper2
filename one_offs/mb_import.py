import pymysql

HOST = 'localhost'
PASSWORD = 'python'
USER = 'python'
DB = 'cpa'
PORT = 3306

with open('mb_cpa.txt', 'r') as f:
    email_bulk = f.readlines()

email_set = email_bulk[0].strip().split()

print(type(email_set))
print(len(email_set))

connection = pymysql.connect(host=HOST,
                             password=PASSWORD,
                             port=PORT,
                             user=USER,
                             db=DB)

sql = 'INSERT INTO emails VALUES (%s)'
with connection.cursor() as cursor:
    for email in email_set:
        try:
            cursor.execute(sql, email)
        except Exception as exc:
            print('Error: %s \nfailed to write %s' % (exc, email))

connection.commit()