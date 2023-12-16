import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple
from database.shop import update_shop_inventory
from utils.cache import CooldownCache


cache = CooldownCache.get_instance()

def check_user_dust_balance(user_id: str, server_id: str, cost: int) -> bool:
    """
    Checks if the user has enough dust to craft a card on a specific server.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID where the user is crafting a card.
        cost (int): The dust cost of the card.

    Returns:
        bool: True if the user has enough dust, False otherwise.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
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
        
        cur.execute("SELECT id FROM Server WHERE serverID = ?", (server_id,))
        if cur.fetchone() is None:
            
            cur.execute("INSERT INTO Server (serverID) VALUES (?)", (server_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def check_user_cooldown(user_id: str, server_id: str) -> Tuple[bool, Optional[datetime.datetime]]:
    """
    Checks if a user is currently under cooldown for random on a specific server.

    Args:
        user_id (str): The user's Discord ID.
        server_id (str): The Discord server's ID.

    Returns:
        Tuple[bool, Optional[datetime.datetime]]: A tuple where the first element is a boolean indicating if the user is under cooldown,
        and the second element is the cooldown end time if they are under cooldown.
    """
    # Check the cache first
    is_on_cooldown, cooldown_end = cache.check_cooldown(user_id, server_id)
    if is_on_cooldown:
        return False, cooldown_end

    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    current_time = datetime.datetime.now()

    try:
        cur.execute("""
        SELECT firstRequestTime, requestCount FROM UserRequests WHERE userID = ? AND serverID = ?
        """, (user_id, server_id))
        row = cur.fetchone()

        if row:
            first_request_time, request_count = row
            first_request_time = datetime.datetime.fromisoformat(first_request_time)

            if current_time - first_request_time < datetime.timedelta(hours=1):
                if request_count >= 5:
                    cooldown_end = first_request_time + datetime.timedelta(hours=1)
                    cache.set_cooldown(user_id, server_id, cooldown_end)  # Update cache
                    return False, cooldown_end  
                else:
                    cur.execute("""
                    UPDATE UserRequests SET requestCount = requestCount + 1 WHERE userID = ? AND serverID = ?
                    """, (user_id, server_id))
            else:
                cur.execute("""
                UPDATE UserRequests SET firstRequestTime = ?, requestCount = 1 WHERE userID = ? AND serverID = ?
                """, (current_time.isoformat(), user_id, server_id))
            conn.commit()
            return True, None  
        else:
            cur.execute("""
            INSERT INTO UserRequests (userID, serverID, firstRequestTime, requestCount) VALUES (?, ?, ?, ?)
            """, (user_id, server_id, current_time.isoformat(), 1))
            conn.commit()
            return True, None  
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False, None  
    finally:
        conn.close()


def check_card_ownership(user_id: str, card_id: int, server_id: str) -> bool:
    """
    Checks if a user already owns a specific card on a specific server.

    Args:
        user_id (str): The user's ID.
        card_id (int): The card's ID.
        server_id (str): The server's ID where the ownership is checked.

    Returns:
        bool: True if the user owns the card, False otherwise.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:

        cur.execute("""
        SELECT 1 FROM UserCard 
        WHERE userID = ? AND serverID = ? AND cardID = ?;
        """, (user_id, server_id, card_id))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()


def get_next_reset_time(server_id: str) -> datetime.datetime:
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    try:
        cur.execute("SELECT lastUpdated FROM Shop WHERE serverID = ?", (server_id,))
        result = cur.fetchone()
        if result:
            last_updated = datetime.datetime.fromisoformat(result[0])
            return last_updated + datetime.timedelta(hours=1)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
    
    return datetime.datetime.now()


def reset_cooldown(user_id: str, server_id: str):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM UserRequests WHERE userID = ? AND serverID = ?", (user_id, server_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def reset_shop(server_id: str):
    """
    Resets the shop for a specific server and triggers an update.

    Args:
        server_id (str): The Discord server's ID.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        
        cur.execute("DELETE FROM Shop WHERE serverID = ?", (server_id,))
        conn.commit()

        
        update_shop_inventory(server_id)
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

