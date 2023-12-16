import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple
from utils.connection import DatabaseConnection

def execute_query(conn, execute_query_sql):
    """ create a table from the execute_query_sql statement
    """
    try:
        c = conn.get_cursor()
        c.execute(execute_query_sql)
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

    
    sql_index_user_on_user_card = "CREATE INDEX IF NOT EXISTS idx_user_on_user_card ON UserCard (userID);"
    sql_index_server_on_user_card = "CREATE INDEX IF NOT EXISTS idx_server_on_user_card ON UserCard (serverID);"
    sql_index_card_on_user_card = "CREATE INDEX IF NOT EXISTS idx_card_on_user_card ON UserCard (cardID);"
    sql_index_user_server_on_user_requests = "CREATE INDEX IF NOT EXISTS idx_user_server_on_user_requests ON UserRequests (userID, serverID);"
    sql_index_user_server_on_dust_balance = "CREATE INDEX IF NOT EXISTS idx_user_server_on_dust_balance ON DustBalance (userID, serverID);"
    
    conn = DatabaseConnection.get_instance()

    
    if conn is not None:
        execute_query(conn, sql_create_server_table)
        execute_query(conn, sql_create_user_table)
        execute_query(conn, sql_create_collection_table)
        execute_query(conn, sql_create_card_table)
        execute_query(conn, sql_create_user_requests_table)  
        execute_query(conn, sql_create_user_card_table)  
        execute_query(conn, sql_create_dust_balance_table)  
        execute_query(conn, sql_create_shop_table)  
        
        execute_query(conn, sql_index_user_on_user_card)
        execute_query(conn, sql_index_server_on_user_card)
        execute_query(conn, sql_index_card_on_user_card)
        execute_query(conn, sql_index_user_server_on_user_requests)
        execute_query(conn, sql_index_user_server_on_dust_balance)
        
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")
