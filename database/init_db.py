import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print("Except :", e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def init_db():
    database = "database.sqlite"

    sql_create_server_table = """CREATE TABLE IF NOT EXISTS Server (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    serverID TEXT UNIQUE
                                );"""

    sql_create_user_table = """CREATE TABLE IF NOT EXISTS User (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    userID TEXT UNIQUE,
                                    serverID INTEGER,
                                    FOREIGN KEY (serverID) REFERENCES Server(id)
                                );"""

    sql_create_collection_table = """CREATE TABLE IF NOT EXISTS Collection (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        name TEXT UNIQUE
                                    );"""

    sql_create_card_table = """CREATE TABLE IF NOT EXISTS Card (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT UNIQUE,
                                    collectionID INTEGER,
                                    rarity TEXT,
                                    title TEXT,
                                    quote TEXT,
                                    imageURL TEXT,
                                    FOREIGN KEY (collectionID) REFERENCES Collection(id),
                                );"""

    sql_create_user_requests_table = """CREATE TABLE IF NOT EXISTS UserRequests (
                                            userID TEXT PRIMARY KEY,
                                            firstRequestTime TIMESTAMP,
                                            requestCount INTEGER
                                        );"""

    sql_create_user_card_table = """CREATE TABLE IF NOT EXISTS UserCard (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            userID INTEGER,
                                            cardID INTEGER,
                                            FOREIGN KEY (userID) REFERENCES User(id),
                                            FOREIGN KEY (cardID) REFERENCES Card(id)
                                        );"""

    sql_create_dust_balance_table = """CREATE TABLE IF NOT EXISTS DustBalance (
                                           userID INTEGER,
                                           serverID INTEGER,
                                           balance INTEGER,
                                           PRIMARY KEY (userID, serverID),
                                           FOREIGN KEY (userID) REFERENCES User(id),
                                           FOREIGN KEY (serverID) REFERENCES Server(id)
                                       );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_server_table)
        create_table(conn, sql_create_user_table)
        create_table(conn, sql_create_collection_table)
        create_table(conn, sql_create_card_table)
        create_table(conn, sql_create_user_requests_table)
        create_table(conn, sql_create_user_card_table)  # New table for user cards
        create_table(conn, sql_create_dust_balance_table)  # New table for dust balance
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")