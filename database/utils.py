import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple

def check_user_dust_balance(user_id: str, cost: int) -> bool:
    """
    Checks if the user has enough dust to craft a card.

    Args:
        user_id (str): The user's ID.
        cost (int): The dust cost of the card.

    Returns:
        bool: True if the user has enough dust, False otherwise.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ?", (user_id,))
        result = cur.fetchone()
        if result:
            return result[0] >= cost
        return False
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

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

