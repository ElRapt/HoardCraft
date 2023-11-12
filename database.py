import sqlite3
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
        print(e)

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
                                    userID INTEGER,
                                    FOREIGN KEY (collectionID) REFERENCES Collection(id),
                                    FOREIGN KEY (userID) REFERENCES User(id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_server_table)
        create_table(conn, sql_create_user_table)
        create_table(conn, sql_create_collection_table)
        create_table(conn, sql_create_card_table)
        conn.commit()
        conn.close()
    else:
        print("Error! cannot create the database connection.")

def get_random_card() -> Optional[Tuple[str, str, str, str, str, str]]:
    """
    Fetches a random card with no owner from the database, including its collection name for the icon.

    Returns:
        A tuple containing the card's name, collection name, title, quote, imageURL, and rarity if found.
        None if no card is available.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    
    try:
        # The SQL query now joins the Card and Collection tables to get the collection name along with the card details
        cur.execute("""
        SELECT c.name, co.name, c.title, c.quote, c.imageURL, c.rarity FROM Card c
        JOIN Collection co ON c.collectionID = co.id
        WHERE c.userID IS NULL
        ORDER BY RANDOM()
        LIMIT 1;
        """)
        card = cur.fetchone()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()
    
    return card if card else None


