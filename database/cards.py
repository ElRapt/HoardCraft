import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple

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


