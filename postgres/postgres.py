import sqlalchemy
from psycopg2 import connect, extensions, sql


conn = connect(
    dbname='test',
    user='postgres',
    host='localhost',
    password='postgres',
)

print(type(conn))
   