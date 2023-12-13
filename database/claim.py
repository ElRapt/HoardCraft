import sqlite3
from sqlite3 import Error

def claim_card(user_id: str, card_id: int, server_id: str) -> bool:
    """
    Claims a card for a user in a specific server. Adds the card to the user's collection in the UserCard table.
    """
    with sqlite3.connect("database.sqlite") as conn:
        cur = conn.cursor()

        try:
            
            cur.execute("""
            SELECT 1 FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = ?;
            """, (user_id, server_id, card_id))
            if cur.fetchone() is not None:
                return False  

            
            cur.execute("""
            INSERT INTO UserCard (userID, serverID, cardID) VALUES (?, ?, ?);
            """, (user_id, server_id, card_id))
            conn.commit()

            return cur.rowcount > 0
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False


def de_claim_card(user_id: str, card_name: str, server_id: str) -> bool:
    """
    De-claims a card for a user in a specific server.
    """
    with sqlite3.connect("database.sqlite") as conn:
        cur = conn.cursor()

        try:
            cur.execute("""
            DELETE FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = (SELECT id FROM Card WHERE name = ?);
            """, (user_id, server_id, card_name))
            conn.commit()

            return cur.rowcount > 0
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return False

