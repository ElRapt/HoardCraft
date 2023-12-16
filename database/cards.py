import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple, List
from utils.connection import DatabaseConnection


def get_random_card() -> Optional[Tuple[int, str, str, str, str, str, str]]:
    """
    Fetches a random card from the database, including its collection name for the icon.

    Returns:
        A tuple containing the card's ID, name, collection name, title, quote, imageURL, and rarity if found.
        None if no card is available.
    """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()
    
    try:
        cursor.execute("""
        SELECT c.id, c.name, co.name, c.title, c.quote, c.imageURL, c.rarity FROM Card c
        JOIN Collection co ON c.collectionID = co.id
        ORDER BY RANDOM()
        LIMIT 1;
        """)
        card = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    return card if card else None

def get_user_collection(user_id: str, server_id: int) -> Optional[list]:
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()
    
    try:
        cursor.execute("""
        SELECT ca.name, co.name, ca.title, ca.quote, ca.imageURL, ca.rarity FROM UserCard uc
        JOIN Card ca ON uc.cardID = ca.id
        JOIN Collection co ON ca.collectionID = co.id
        WHERE uc.userID = ? AND uc.serverID = ?
        ORDER BY CASE ca.rarity
            WHEN 'legendary' THEN 1
            WHEN 'epic' THEN 2
            WHEN 'rare' THEN 3
            WHEN 'uncommon' THEN 4
            WHEN 'common' THEN 5
        END, ca.name;
        """, (user_id, server_id))
        cards = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None

    
    return cards if cards else None


def get_collections() -> List[str]:
    """ Fetch all distinct collections from the database. """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()

    try:
        cursor.execute("SELECT DISTINCT name FROM Collection")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []


        
def fetch_cards_by_collection(user_id: str, collection_name: str) -> List[Tuple]:
    db_connection = DatabaseConnection.get_instance()
    cur = db_connection.get_cursor()
    try:
            cur.execute("""
            SELECT c.name, co.name, c.title, c.quote, c.imageURL, c.rarity 
            FROM Card c
            JOIN Collection co ON c.collectionID = co.id
            JOIN UserCard uc ON c.id = uc.cardID
            WHERE uc.userID = ? AND LOWER(co.name) = LOWER(?)
            ORDER BY CASE c.rarity
                WHEN 'legendary' THEN 1
                WHEN 'epic' THEN 2
                WHEN 'rare' THEN 3
                WHEN 'uncommon' THEN 4
                WHEN 'common' THEN 5
            END, c.name;
            """, (user_id, collection_name))
            cards = cur.fetchall()
            return cards
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []


