import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple

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

