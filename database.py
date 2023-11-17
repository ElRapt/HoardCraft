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


def get_random_card() -> Optional[Tuple[int, str, str, str, str, str, str]]:
    """
    Fetches a random card from the database, including its collection name for the icon.

    Returns:
        A tuple containing the card's ID, name, collection name, title, quote, imageURL, and rarity if found.
        None if no card is available.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        SELECT c.id, c.name, co.name, c.title, c.quote, c.imageURL, c.rarity FROM Card c
        JOIN Collection co ON c.collectionID = co.id
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


def claim_card(user_id: str, card_id: int, server_id: str) -> bool:
    """
    Claims a card for a user in a specific server. Adds the card to the user's collection in the UserCard table.

    Args:
        user_id (str): The user's ID.
        card_id (int): The ID of the card being claimed.
        server_id (str): The server's ID where the card is being claimed.

    Returns:
        True if the card was successfully claimed.
        False if the card is already claimed by the user or does not exist.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        # Check if user exists
        cur.execute("SELECT id FROM User WHERE userID = ? AND serverId = ?", (user_id, server_id))
        user_row = cur.fetchone()

        if user_row is None:
            # Create a new user if not exists
            cur.execute("INSERT INTO User (userID, serverID) VALUES (?, ?)", (user_id, server_id))
            user_db_id = cur.lastrowid
        else:
            user_db_id = user_row[0]

        # Check if the card is already claimed by the user
        cur.execute("SELECT id FROM UserCard WHERE userID = ? AND cardID = ?", (user_db_id, card_id))
        if cur.fetchone() is not None:
            return False  # Card already claimed by this user

        # Claim the card
        cur.execute("INSERT INTO UserCard (userID, cardID) VALUES (?, ?)", (user_db_id, card_id))
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
        cur.execute("""
        SELECT ca.name, co.name, ca.title, ca.quote, ca.imageURL, ca.rarity FROM UserCard uc
        JOIN Card ca ON uc.cardID = ca.id
        JOIN Collection co ON ca.collectionID = co.id
        JOIN User u ON uc.userID = u.id
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

def de_claim_card(user_id: str, card_name: str, server_id: str) -> bool:
    """
    De-claims a card for a user in a specific server.

    Args:
        user_id (str): The user's ID.
        card_name (str): The card's name.
        server_id (str): The server's ID.

    Returns:
        True if the card was successfully de-claimed.
        False if an error occurs.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:

        cur.execute("""
        DELETE FROM UserCard WHERE userID = (SELECT id FROM User WHERE userID = ? AND serverID = ?) AND cardID = (SELECT id FROM Card WHERE name = ?);
        """, (user_id, server_id, card_name))
        conn.commit()

        return cur.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()


def check_user_cooldown(user_id: str):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    current_time = datetime.datetime.now()

    try:
        cur.execute("SELECT firstRequestTime, requestCount FROM UserRequests WHERE userID = ?", (user_id,))
        row = cur.fetchone()
        if row:
            first_request_time, request_count = row
            first_request_time = datetime.datetime.fromisoformat(first_request_time)

            if current_time - first_request_time < datetime.timedelta(hours=1):
                if request_count >= 5:
                    cooldown_end = first_request_time + datetime.timedelta(hours=1)
                    return False, cooldown_end  # Cooldown active, return end time
                else:
                    cur.execute("UPDATE UserRequests SET requestCount = requestCount + 1 WHERE userID = ?", (user_id,))
            else:
                cur.execute("UPDATE UserRequests SET firstRequestTime = ?, requestCount = 1 WHERE userID = ?", (current_time.isoformat(), user_id))
            conn.commit()
            return True, None  # No cooldown
        else:
            cur.execute("INSERT INTO UserRequests (userID, firstRequestTime, requestCount) VALUES (?, ?, ?)", (user_id, current_time.isoformat(), 1))
            conn.commit()
            return True, None  # No cooldown
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False, None  # Default to cooldown in case of error
    finally:
        conn.close()

def check_card_ownership(user_id: str, card_id: int) -> bool:
    """
    Checks if a user already owns a specific card.

    Args:
        user_id (str): The user's ID.
        card_id (int): The card's ID.

    Returns:
        bool: True if the user owns the card, False otherwise.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        # Query the UserCard table to check if the user already owns this card
        cur.execute("""
        SELECT id FROM UserCard 
        WHERE userID = (SELECT id FROM User WHERE userID = ?) 
        AND cardID = ?;
        """, (user_id, card_id))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()



def calculate_dust_earned(rarity: str) -> int:
    """
    Calculate the amount of dust earned based on the card's rarity.

    Args:
        rarity (str): The rarity of the card.

    Returns:
        int: The amount of dust earned.
    """
    dust_values = {
        'legendary': 500,  # TODO: Update with actual value
        'epic': 200,       # TODO: Update with actual value
        'rare': 100,       # TODO: Update with actual value
        'uncommon': 50,   # TODO: Update with actual value
        'common': 10,     # TODO: Update with actual value
    }
    return dust_values.get(rarity.lower(), 0)  # Default to 0 if rarity not found

def update_dust_balance(user_id: str, server_id: str, dust_earned: int):
    """
    Update the user's dust balance.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID.
        dust_earned (int): The amount of dust to add to the balance.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        # Check if the user has a dust balance entry
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cur.fetchone()
        if result:
            # Update existing balance
            new_balance = result[0] + dust_earned
            cur.execute("UPDATE DustBalance SET balance = ? WHERE userID = ? AND serverID = ?", (new_balance, user_id, server_id))
        else:
            # Create new balance entry
            cur.execute("INSERT INTO DustBalance (userID, serverID, balance) VALUES (?, ?, ?)", (user_id, server_id, dust_earned))

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



def get_dust_balance(user_id: str, server_id: str) -> int:
    """
    Retrieves the dust balance for a user in a specific server.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID.

    Returns:
        int: The user's dust balance.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cur.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return 0
    finally:
        conn.close()



## HACK: This is a temporary function to reset the cooldown for the user
def reset_cooldown(user_id: str):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM UserRequests WHERE userID = ?", (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



