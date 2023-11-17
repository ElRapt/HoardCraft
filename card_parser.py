import sqlite3

def add_card_to_db(name, collection_id, rarity, title, quote, image_url):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Card (name, collectionID, rarity, title, quote, imageURL) VALUES (?, ?, ?, ?, ?, ?)", (name, collection_id, rarity, title, quote, image_url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def process_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            # Assuming each line is: name, collection_id, rarity, title, quote, image_url
            parts = line.strip().split(',')
            if len(parts) == 6:
                add_card_to_db(*parts)
            else:
                print(f"Skipping invalid line: {line}")

if __name__ == "__main__":
    file_path = 'path_to_your_txt_file.txt'  # Replace with your file path
    process_file(file_path)
