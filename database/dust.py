import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional, Tuple
from utils.connection import DatabaseConnection

def get_dust_balance(user_id: str, server_id: str) -> int:
    """
    Retrieves the dust balance for a user in a specific server.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID.

    Returns:
        int: The user's dust balance.
    """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()

    try:
        cursor.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return 0

def calculate_dust_earned(rarity: str) -> int:
    """
    Calculate the amount of dust earned based on the card's rarity.

    Args:
        rarity (str): The rarity of the card.

    Returns:
        int: The amount of dust earned.
    """
    dust_values = {
        'legendary': 500,  
        'epic': 200,       
        'rare': 100,       
        'uncommon': 50,   
        'common': 10,     
    }
    return dust_values.get(rarity.lower(), 0)  

def update_dust_balance(user_id: str, server_id: str, dust_earned: int):
    """
    Update the user's dust balance.

    Args:
        user_id (str): The user's ID.
        server_id (str): The server's ID.
        dust_earned (int): The amount of dust to add to the balance.
    """
    db_connection = DatabaseConnection.get_instance()
    cursor = db_connection.get_cursor()

    try:
        
        cursor.execute("SELECT balance FROM DustBalance WHERE userID = ? AND serverID = ?", (user_id, server_id))
        result = cursor.fetchone()
        if result:
            
            new_balance = result[0] + dust_earned
            cursor.execute("UPDATE DustBalance SET balance = ? WHERE userID = ? AND serverID = ?", (new_balance, user_id, server_id))
        else:
            
            cursor.execute("INSERT INTO DustBalance (userID, serverID, balance) VALUES (?, ?, ?)", (user_id, server_id, dust_earned))

        db_connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
