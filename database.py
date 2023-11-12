import sqlite3
from sqlite3 import Error

def init_db():
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    create_server_table_sql = """
    CREATE TABLE IF NOT EXISTS Server (
        serverID TEXT PRIMARY KEY,
        users TEXT
    );
    """

    create_user_table_sql = """
    CREATE TABLE IF NOT EXISTS User (
        userID TEXT PRIMARY KEY,
        cards TEXT
    );
    """

    create_collection_table_sql = """
    CREATE TABLE IF NOT EXISTS Collection (
        name TEXT PRIMARY KEY,
        cards TEXT
    );
    """

    create_card_table_sql = """
    CREATE TABLE IF NOT EXISTS Card (
        name TEXT PRIMARY KEY,
        collection TEXT,
        rarity TEXT,
        title TEXT,
        quote TEXT,
        imageURL TEXT,
        owner TEXT,
        FOREIGN KEY (collection) REFERENCES Collection(name),
        FOREIGN KEY (owner) REFERENCES User(userID)
    );
    """


    cur.execute(create_server_table_sql)
    cur.execute(create_user_table_sql)
    cur.execute(create_collection_table_sql)
    cur.execute(create_card_table_sql)


    con.commit()

    con.close()

init_db()



