import sqlite3
from sqlite3 import Error
from utils.connection import DatabaseConnection

def claim_card(user_id: str, card_id: int, server_id: str) -> bool:
    """
    Claims a card for a user in a specific server. Adds the card to the user's collection in the UserCard table.
    """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()
    try:
        
        cursor.execute("""
        SELECT 1 FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = ?;
        """, (user_id, server_id, card_id))
        if cursor.fetchone() is not None:
            return False  

        
        cursor.execute("""
        INSERT INTO UserCard (userID, serverID, cardID) VALUES (?, ?, ?);
        """, (user_id, server_id, card_id))
        db_connection.commit()

        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False


def de_claim_card(user_id: str, card_name: str, server_id: str) -> bool:
    """
    De-claims a card for a user in a specific server.
    """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()

    try:
        cursor.execute("""
        DELETE FROM UserCard WHERE userID = ? AND serverID = ? AND cardID = (SELECT id FROM Card WHERE name = ?);
        """, (user_id, server_id, card_name))
        db_connection.commit()

        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False

