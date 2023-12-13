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
                                    userID TEXT,
                                    serverID INTEGER,
                                    PRIMARY KEY (userID, serverID),
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
                                    FOREIGN KEY (collectionID) REFERENCES Collection(id)
                                );"""

    
    sql_create_user_requests_table = """CREATE TABLE IF NOT EXISTS UserRequests (
                                            userID TEXT,
                                            serverID TEXT,
                                            firstRequestTime TIMESTAMP,
                                            requestCount INTEGER,
                                            PRIMARY KEY (userID, serverID),
                                            FOREIGN KEY (userID, serverID) REFERENCES User(userID, serverID)
                                        );"""

    
    sql_create_user_card_table = """CREATE TABLE IF NOT EXISTS UserCard (
                                            userID TEXT NOT NULL,
                                            serverID INTEGER NOT NULL,
                                            cardID INTEGER NOT NULL,
                                            PRIMARY KEY (userID, serverID, cardID),
                                            FOREIGN KEY (userID, serverID) REFERENCES User(userID, serverID),
                                            FOREIGN KEY (cardID) REFERENCES Card(id)
                                        );"""

    sql_create_dust_balance_table = """CREATE TABLE IF NOT EXISTS DustBalance (
                                           userID TEXT NOT NULL,
                                           serverID INTEGER NOT NULL,
                                           balance INTEGER,
                                           PRIMARY KEY (userID, serverID),
                                           FOREIGN KEY (userID, serverID) REFERENCES User(userID, serverID),
                                           FOREIGN KEY (serverID) REFERENCES Server(id)
                                       );"""
                                       
    
    sql_create_shop_table = """CREATE TABLE IF NOT EXISTS Shop (
                                        serverID INTEGER PRIMARY KEY,
                                        lastUpdated TIMESTAMP,
                                        item1 INTEGER,
                                        item2 INTEGER,
                                        item3 INTEGER,
                                        FOREIGN KEY(item1) REFERENCES Card(id),
                                        FOREIGN KEY(item2) REFERENCES Card(id),
                                        FOREIGN KEY(item3) REFERENCES Card(id)
                                    );"""

    
    conn = create_connection(database)

    
    if conn is not None:
        create_table(conn, sql_create_server_table)
        create_table(conn, sql_create_user_table)
        create_table(conn, sql_create_collection_table)
        create_table(conn, sql_create_card_table)
        create_table(conn, sql_create_user_requests_table)  
        create_table(conn, sql_create_user_card_table)  
        create_table(conn, sql_create_dust_balance_table)  
        create_table(conn, sql_create_shop_table)  
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")
