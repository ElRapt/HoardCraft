import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple, List

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

def get_user_collection(user_id: str, server_id: int) -> Optional[list]:
    """
    Fetches the user's collection in a specific server.

    Args:
        user_id (str): The user's Discord ID.
        server_id (int): The Discord server's ID where the collection is being fetched.

    Returns:
        A list of tuples containing the card's name, collection name, title, quote, imageURL, and rarity if found.
        None if no cards are available.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        SELECT ca.name, co.name, ca.title, ca.quote, ca.imageURL, ca.rarity FROM UserCard uc
        JOIN Card ca ON uc.cardID = ca.id
        JOIN Collection co ON ca.collectionID = co.id
        WHERE uc.userID = ? AND uc.serverID = ?;
        """, (user_id, server_id))
        cards = cur.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()
    
    return cards if cards else None


def get_collections() -> List[str]:
    """ Fetch all distinct collections from the database. """
    conn = sqlite3.connect("database.sqlite")
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT name from Collection")
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()
        
def fetch_cards_by_collection(user_id: str, collection_name: str) -> List[Tuple]:
    """ Fetch cards for a specific user filtered by collection name. """
    conn = sqlite3.connect("database.sqlite")
    try:
        with conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT c.name, co.name, c.title, c.quote, c.imageURL, c.rarity 
            FROM Card c
            JOIN Collection co ON c.collectionID = co.id
            JOIN UserCard uc ON c.id = uc.cardID
            WHERE uc.userID = ? AND LOWER(co.name) = LOWER(?)
            """, (user_id, collection_name))
            cards = cur.fetchall()
            return cards
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

