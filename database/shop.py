import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple


def craft_card(user_id: str, card_id: int, server_id: int, cost: int) -> bool:
    """
    Handles the crafting of a card for a user.

    Args:
        user_id (str): The user's ID.
        card_id (int): The ID of the card being crafted.
        server_id (int): The ID of the server where the card is being crafted.
        cost (int): The dust cost of the card.

    Returns:
        bool: True if crafting was successful, False otherwise.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cur.fetchone()
        if result and result[0] >= cost:
            new_balance = result[0] - cost
            cur.execute("UPDATE DustBalance SET balance = ? WHERE userID = ? AND serverID = ?", (new_balance, user_id, server_id))
        else:
            return False  

        
        cur.execute("SELECT 1 FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = ?", (user_id, server_id, card_id))
        if cur.fetchone() is not None:
            return False  

        
        cur.execute("INSERT INTO UserCard (userID, serverID, cardID) VALUES (?, ?, ?)", (user_id, server_id, card_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()


import datetime

last_updated_cache = {}  

def get_shop_inventory(server_id: str) -> list:
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    current_time = datetime.datetime.now()

    try:
        
        last_updated = last_updated_cache.get(server_id)
        if last_updated is None or current_time - last_updated >= datetime.timedelta(hours=1):
            update_shop_inventory(server_id)
            last_updated = datetime.datetime.now()
            last_updated_cache[server_id] = last_updated

        
        cur.execute("""
        SELECT c.id, c.name, co.name, c.title, c.quote, c.imageURL, c.rarity,
               (CASE c.rarity WHEN 'legendary' THEN 1000 WHEN 'epic' THEN 400 WHEN 'rare' THEN 200 WHEN 'uncommon' THEN 100 ELSE 50 END) as cost
        FROM Shop s
        JOIN Card c ON c.id IN (s.item1, s.item2, s.item3)
        JOIN Collection co ON c.collectionID = co.id
        WHERE s.serverID = ?
        """, (server_id,))
        cards = cur.fetchall()
        return cards

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()



def update_shop_inventory(server_id: int):
    """
    Updates the shop inventory for a specific server.

    Args:
        server_id (int): The ID of the server.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        
        cur.execute("""
        SELECT id FROM Card
        ORDER BY RANDOM()
        LIMIT 3
        """)
        items = [item[0] for item in cur.fetchall()]

        
        cur.execute("""
        INSERT INTO Shop (serverID, lastUpdated, item1, item2, item3)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(serverID)
        DO UPDATE SET lastUpdated = CURRENT_TIMESTAMP, item1 = ?, item2 = ?, item3 = ?
        """, (server_id, datetime.datetime.now(), *items, *items))

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
