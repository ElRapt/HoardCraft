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

def claim_card(user_id: str, card_name: str, server_id: str) -> bool:
    """
    Claims a card for a user in a specific server. If the user does not exist, creates a new user.

    Args:
        user_id (str): The user's ID.
        card_name (str): The card's name.
        server_id (str): The server's ID where the card is being claimed.

    Returns:
        True if the card was successfully claimed.
        False if the card is already claimed or does not exist.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        # Check if user exists
        cur.execute("SELECT id FROM User WHERE userID = ? AND serverId = ?", (user_id, server_id))
        user_exists = cur.fetchone()

        if user_exists is None:
            # Create a new user if not exists
            cur.execute("INSERT INTO User (userID, serverID) VALUES (?, ?)", (user_id, server_id))

        # Now claim the card
        cur.execute("""
        UPDATE Card SET userID = (SELECT id FROM User WHERE userID = ? AND serverID = ?) WHERE name = ? AND userID IS NULL;
        """, (user_id, server_id, card_name))
        conn.commit()

        return cur.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

def get_user_collection(user_id: str, server_id: str) -> Optional[list]:
    """
    Fetches the user's collection in a specific server.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID where the collection is being fetched.

    Returns:
        A list of tuples containing the card's name, collection name, title, quote, imageURL, and rarity if found.
        None if no card is available.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    
    try:
        # The SQL query now joins the Card and Collection tables to get the collection name along with the card details
        cur.execute("""
        SELECT c.name, co.name, c.title, c.quote, c.imageURL, c.rarity FROM Card c
        JOIN Collection co ON c.collectionID = co.id
        JOIN User u ON c.userID = u.id
        WHERE u.userID = ? AND u.serverID = ?;
        """, (user_id, server_id))
        cards = cur.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()
    
    return cards if cards else None

def ensure_server_exists_in_db(server_id: str):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        # Check if the server exists in the database
        cur.execute("SELECT id FROM Server WHERE serverID = ?", (server_id,))
        if cur.fetchone() is None:
            # If not, add it
            cur.execute("INSERT INTO Server (serverID) VALUES (?)", (server_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()