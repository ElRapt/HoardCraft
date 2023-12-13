
import sqlite3
import csv

def add_card_to_db(name, collection_id, rarity, title, quote, image_url):
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    try:
        
        cur.execute("SELECT * FROM Card WHERE name = ?", (name,))
        if cur.fetchone():
            print(f"Updating card with name '{name}'.")
            cur.execute("UPDATE Card SET collectionID = ?, rarity = ?, title = ?, quote = ?, imageURL = ? WHERE name = ?", (collection_id, rarity, title, quote, image_url, name))
        else:
            cur.execute("INSERT INTO Card (name, collectionID, rarity, title, quote, imageURL) VALUES (?, ?, ?, ?, ?, ?)", (name, collection_id, rarity, title, quote, image_url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



import csv

def adjusted_custom_parser(line):
    
    reader = csv.reader([line], skipinitialspace=True)
    for row in reader:
        
        if len(row) == 6:
            return [field.strip() for field in row]

    
    
    parts = line.split(',')
    if len(parts) < 6:
        return None

    
    name = parts[0].strip()
    collection_id = parts[1].strip()
    rarity = parts[2].strip()
    title = parts[3].strip()

    
    image_url = parts[-1].strip()

    
    quote = ','.join(parts[4:-1]).strip()

    return name, collection_id, rarity, title, quote, image_url




def delete_encoding_errors():
    conn = sqlite3.connect("database.sqlite")
    cur = conn.cursor()
    try:
        
        cur.execute("DELETE FROM Card WHERE name LIKE '%lâ€™%' OR title LIKE '%lâ€™%' OR quote LIKE '%lâ€™%'")
        conn.commit()
        print(f"Deleted entries with encoding errors.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()



def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parsed_line = adjusted_custom_parser(line)
            if parsed_line:
                add_card_to_db(*parsed_line)
            else:
                print(f"Skipping invalid line: {line.strip()}")

if __name__ == "__main__":
    file_path = 'cards.csv'  
    delete_encoding_errors()
    process_file(file_path)
