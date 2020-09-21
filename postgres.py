import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    plan = Column(String)

    def __repr__(self):
        return f"<Users(username='{self.username}', password='{self.password}', plan='{self.plan}')>"


def connect():
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(user="admin",
                                      password="admin",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    return connection, cursor


def insert(table: str, **kwargs):
    connection, cursor = connect()
    cols = ','.join(kwargs['columns'])
    vals = ','.join(kwargs['values'])
    try:
        cursor.execute(
            f"INSERT INTO {table} {cols} VALUES {vals}"
        )
        print(f"Inserted data into {table}")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while inserting to {table}", error)
    finally:
        close(connection, cursor)


def close(connection, cursor):
    cursor.close()
    connection.close()
    print("PostgreSQL connection is closed")


if __name__ == '__main__':
    insert('users', columns=('user_id', 'username', 'password'), values=('1', '2', '3'))
