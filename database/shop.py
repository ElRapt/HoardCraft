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
        # Check and update the user's dust balance
        cur.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cur.fetchone()
        if result and result[0] >= cost:
            new_balance = result[0] - cost
            cur.execute("UPDATE DustBalance SET balance = ? WHERE userID = ? AND serverID = ?", (new_balance, user_id, server_id))
        else:
            return False  # Not enough dust

        # Check if the user already owns the card
        cur.execute("SELECT 1 FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = ?", (user_id, server_id, card_id))
        if cur.fetchone() is not None:
            return False  # User already owns the card

        # Add the card to the user's collection
        cur.execute("INSERT INTO UserCard (userID, serverID, cardID) VALUES (?, ?, ?)", (user_id, server_id, card_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()


def get_shop_inventory() -> list:
    """
    Retrieves the current inventory of cards in the shop.

    Returns:
        list: A list of tuples representing the cards in the shop.
    """
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()

    try:
        cur.execute("""
        SELECT c.id, c.name, co.name, c.title, c.quote, c.imageURL, c.rarity, (CASE c.rarity WHEN 'legendary' THEN 1000 WHEN 'epic' THEN 400 WHEN 'rare' THEN 200 WHEN 'uncommon' THEN 100 ELSE 50 END) as cost
        FROM Card c
        JOIN Collection co ON c.collectionID = co.id
        ORDER BY RANDOM()
        LIMIT 3;
        """)
        cards = cur.fetchall()
        return cards
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

