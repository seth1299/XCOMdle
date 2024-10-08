import sqlite3
from bs4 import BeautifulSoup
import requests

ranks = ["Squaddie", "Corporal", "Sergeant", "Lieutenant", "Captain", "Major", "Colonel"]
psionic_ranks = ["Psi Adept", "Psi Specialist", "Psi Operative"]
globalRankIndex = 0

# Function to create a connection to SQLite database
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('xcom_abilities.db')  # Database will be created if it doesn't exist
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

# Function to create the abilities table
def create_table(conn):
    try:
        cursor = conn.cursor()
        # Drop the existing table if it exists
        cursor.execute('DROP TABLE IF EXISTS abilities')
        
        # Create the table with the new schema
        sql_create_table = '''
        CREATE TABLE IF NOT EXISTS abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            rank TEXT NOT NULL,
            game1 TEXT NOT NULL,
            game2 TEXT
        );
        '''
        cursor.execute(sql_create_table)
        print("Table created successfully")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


# Function to insert ability data into the table
def insert_ability(conn, ability):
    global globalRankIndex
    if len(ability) > 4:
        try:
            sql_insert_ability = '''
            INSERT INTO abilities (name, class, rank, game1, game2)
            VALUES (?, ?, ?, ?, ?);
            '''
            cursor = conn.cursor()
            cursor.execute(sql_insert_ability, ability)
            conn.commit()
            print(f"Ability {ability} inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting ability: {e}")
    else:
        try:
            sql_insert_ability = '''
            INSERT INTO abilities (name, class, rank, game1)
            VALUES (?, ?, ?, ?);
            '''
            cursor = conn.cursor()
            cursor.execute(sql_insert_ability, ability)
            conn.commit()
            print(f"Ability {ability} inserted successfully")
        except sqlite3.Error as e:
            print(f"Error inserting ability: {e}")
        
def get_rank(text):
    for rank in ranks:
        if rank in str(text):
            return rank
    
    return ""

# Scraping for XCOM: Enemy Unknown/Enemy Within classes
def scrape_data(conn, class_name, url, game1, game2 = None):
    global globalRankIndex
    globalRankIndex = 0
    
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the header for "Abilities"
        abilities_header = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'Abilities' in tag.get_text())
        
        if game1 != "XCOM 2":
            if abilities_header:
                # Get the next table after the "Abilities" header
                abilities_table = abilities_header.find_next('table')
                if abilities_table:
                    rows = abilities_table.find_all('tr')
                    rows = enumerate(rows, 1)
                    #print(str(rows))
                    
                    for index, row in rows:
                        print("")
                        print("Index: ", index)
                        columns = row.find_all('td')
                        howManyColumns = 0
                        for column in columns:
                            columnString = str(column)
                            if howManyColumns >= 2:
                                break
                            if "title" not in columnString:
                                continue
                            name = ""
                            start = int(columnString.index("title"))
                            start += len("title") + 2
                            name = columnString[start:]
                            end = name.index("\"", 1)
                            name = name[0:end]
                            #print(f"Preparing to add {name} at column position {howManyColumns}!")
                            if "rank" in name:
                                pass
                            else:
                                if ":" in name or "Defense" in name or "Critical" in name:
                                    continue
                                if "(" in name:
                                    name = name[0:name.index("(")]
                                name = name.strip()
                                if "&amp;" in name:
                                    name = name.replace('&amp;', '&')
                                
                                if globalRankIndex >= len(ranks):
                                    if game2 != None:
                                        ability = (name, class_name, ranks[len(ranks) - 1], game1, game2)
                                    else:
                                        ability = (name, class_name, ranks[len(ranks) - 1], game1, "N/A")
                                    
                                else:
                                    if game2 != None:
                                        ability = (name, class_name, ranks[globalRankIndex], game1, game2)
                                    else:
                                        ability = (name, class_name, ranks[globalRankIndex], game1, "N/A")
                                    
                                insert_ability(conn, ability)  
                                
                            howManyColumns += 1
                            
                        if index % 2 == 0 or index == 11:
                                globalRankIndex += 1                        
                else:
                    print(f"Could not find ability table for {class_name}")
            else:
                print(f"Could not find 'Abilities' header for {class_name}")
                
        else:
            if abilities_header:
                
                # Get the next table after the "Abilities" header
                abilities_table = abilities_header.find_next('table')
                if abilities_table:
                    rows = abilities_table.find_all('tr')
                    rows = enumerate(rows, 1)
                    #print(str(rows))
                    
                    for index, row in rows:
                        name = ""
                        print("")
                        print("Index: ", index)
                        columns = row.find_all('td')
                        #print(columns)
                        howManyColumns = 0
                        abilities_added_this_rank = 0
                        for column in columns:
                            columnString = str(column)
                            if howManyColumns >= 2:
                                break
                            if class_name == "Ranger":
                                if "span id" not in columnString:
                                    continue
                                name = ""
                                start = int(columnString.index("span id"))
                                start += len("span id") + 2
                                name = columnString[start:]
                                end = name.index("\"", 1)
                                name = name[0:end]
                                temp_string = name[0].upper() + name[1:]
                                name = temp_string
                                #print(f"Preparing to add {name} at column position {howManyColumns}!")
                                if "rank" in name:
                                    pass
                                else:
                                    if ":" in name:
                                        continue
                                    if "(" in name:
                                        name = name[0:name.index("(")]
                                    name = name.strip()
                                    if "&amp;" in name:
                                        name = name.replace('&amp;', '&')
                                    if "_" in name:
                                        number_of_spaces = name.count('_')
                                        while number_of_spaces > 0:
                                            temp_index = name.index('_')
                                            name = name.replace('_', " ", 1)
                                            temp_string = name[0 : temp_index + 1] + name[temp_index + 1].upper() + name[temp_index + 2:]
                                            name = temp_string
                                            number_of_spaces -= 1
                                    
                                    if globalRankIndex >= len(ranks):
                                        if game2 != None:
                                            ability = (name, class_name, ranks[len(ranks) - 1], game1, game2)
                                        else:
                                            ability = (name, class_name, ranks[len(ranks) - 1], game1)
                                        
                                    else:
                                        if game2 != None:
                                            ability = (name, class_name, ranks[globalRankIndex], game1, game2)
                                        else:
                                            ability = (name, class_name, ranks[globalRankIndex], game1)
                                    
                                    abilities_added_this_rank += 1
                                    insert_ability(conn, ability)
                                    
                            else:
                                start = 0
                                if index == 3 and abilities_added_this_rank == 1:
                                    continue
                                if "<b>" not in columnString:
                                    continue
                                    '''
                                    if index == 3:
                                        start = int(columnString.index("<td>"))
                                        start += len("<td>")
                                        name = columnString[start:]
                                        name = name.strip()
                                        end = name.index("</td>")
                                        name = name[0:end]
                                        temp_string = name[0].upper() + name[1:]
                                        name = temp_string
                                    else:
                                        continue
                                    '''
                                else:
                                    name = ""
                                    start = columnString.index("<b>")
                                    start += len("<b>")
                                    name = columnString[start:]
                                    name = name.strip()
                                    end = name.index("</b>")
                                    name = name[0:end]
                                    temp_string = name[0].upper() + name[1:]
                                    name = temp_string
                                    
                                #print(f"Preparing to add {name} at column position {howManyColumns}!")
                                if get_rank(name) != "":
                                    pass
                                else:
                                    if ":" in name:
                                        continue
                                    if "(" in name:
                                        name = name[0:name.index("(")]
                                    name = name.strip()
                                    if "&amp;" in name:
                                        name = name.replace('&amp;', '&')
                                    if "_" in name:
                                        number_of_spaces = name.count('_')
                                        while number_of_spaces > 0:
                                            temp_index = name.index('_')
                                            name = name.replace('_', " ", 1)
                                            temp_string = name[0 : temp_index + 1] + name[temp_index + 1].upper() + name[temp_index + 2:]
                                            name = temp_string
                                            number_of_spaces -= 1
                                    
                                    if globalRankIndex >= len(ranks):
                                        if game2 != None:
                                            ability = (name, class_name, ranks[len(ranks) - 1], game1, game2)
                                        else:
                                            ability = (name, class_name, ranks[len(ranks) - 1], game1)
                                        
                                    else:
                                        if game2 != None:
                                            ability = (name, class_name, ranks[globalRankIndex], game1, game2)
                                        else:
                                            ability = (name, class_name, ranks[globalRankIndex], game1)
                                    
                                    abilities_added_this_rank += 1
                                    insert_ability(conn, ability)
                                      
                                
                            howManyColumns += 1
                            
                        if abilities_added_this_rank == 2 or index == 3:
                                globalRankIndex += 1
                                abilities_added_this_rank = 0                        
                else:
                    print(f"Could not find ability table for {class_name}")
            else:
                print(f"Could not find 'Abilities' header for {class_name}")
    else:
        print(f"Failed to retrieve data from {url}")
    
    abilities_added_this_rank = 0
    globalRankIndex = 0

def add_hard_coded_classes(conn):
    # MEC Trooper from XCOM: Enemy Within
    
    insert_ability(conn, ("Collateral Damage", "MEC Trooper", "Squaddie", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Advanced Fire Control", "MEC Trooper", "Corporal", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Automated Threat Assessment", "MEC Trooper", "Corporal", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Vital-Point Targeting", "MEC Trooper", "Sergeant", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Damage Control", "MEC Trooper", "Sergeant", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Jetboot Module", "MEC Trooper", "Lieutenant", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("One For All", "MEC Trooper", "Lieutenant", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Repair Servos", "MEC Trooper", "Captain", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Expanded Storage", "MEC Trooper", "Captain", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Overdrive", "MEC Trooper", "Major", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Absorption Fields", "MEC Trooper", "Colonel", 'XCOM: Enemy Within', 'N/A'))
    insert_ability(conn, ("Reactive Targeting Sensors", "MEC Trooper", "Colonel", 'XCOM: Enemy Within', 'N/A'))
    
    # Psionic from XCOM: Enemy Unknown and XCOM: Enemy Within
    insert_ability(conn, ("Mindfray", "Psionic", "Psi Adept", 'XCOM: Enemy Unknown', 'XCOM: Enemy Within'))
    insert_ability(conn, ("Psi Inspiration", "Psionic", "Psi Specialist", 'XCOM: Enemy Unknown', 'XCOM: Enemy Within'))
    insert_ability(conn, ("Psi Panic", "Psionic", "Psi Specialist", 'XCOM: Enemy Unknown', 'XCOM: Enemy Within'))
    insert_ability(conn, ("Telekinetic Field", "Psionic", "Psi Operative", 'XCOM: Enemy Unknown', 'XCOM: Enemy Within'))
    insert_ability(conn, ("Mind Control", "Psionic", "Psi Operative", 'XCOM: Enemy Unknown', 'XCOM: Enemy Within'))
    
    # Psi Operative from XCOM 2
    insert_ability(conn, ("Soulfire", "Psi Operative", "Initiate", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Stasis", "Psi Operative", "Initiate", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Insanity", "Psi Operative", "Acolyte", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Inspire", "Psi Operative", "Acolyte", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Soul Steal", "Psi Operative", "Adept", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Stasis Shield", "Psi Operative", "Adept", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Solace", "Psi Operative", "Disciple", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Sustain", "Psi Operative", "Disciple", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Schism", "Psi Operative", "Mystic", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Fortress", "Psi Operative", "Mystic", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Fuse", "Psi Operative", "Warlock", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Domination", "Psi Operative", "Warlock", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Null Lance", "Psi Operative", "Magus", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Void Rift", "Psi Operative", "Magus", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    
    # SPARK from XCOM 2
    insert_ability(conn, ("Overdrive", "SPARK", "Squire", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Bulwark", "SPARK", "Aspirant", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Adaptive Aim", "SPARK", "Aspirant", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Rainmaker", "SPARK", "Knight", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Strike", "SPARK", "Knight", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Intimidate", "SPARK", "Cavalier", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Wrecking Ball", "SPARK", "Cavalier", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Repair", "SPARK", "Vanguard", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Bombard", "SPARK", "Vanguard", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Channeling Field", "SPARK", "Paladin", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Hunter Protocol", "SPARK", "Paladin", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Sacrifice", "SPARK", "Champion", 'XCOM 2', 'XCOM 2: War of the Chosen'))
    insert_ability(conn, ("Nova", "SPARK", "Champion", 'XCOM 2', 'XCOM 2: War of the Chosen'))

# Main workflow
def main():
    # Create a database connection
    conn = create_connection()    

    if conn is not None:
        # Create the table
        create_table(conn)

        # Scrape data for XCOM: Enemy Unknown/Within classes
        scrape_data(conn, 'Assault', 'https://xcom.fandom.com/wiki/Assault_Class', 'XCOM: Enemy Unknown', 'XCOM: Enemy Within')
        scrape_data(conn, 'Heavy', 'https://xcom.fandom.com/wiki/Heavy_Class', 'XCOM: Enemy Unknown', 'XCOM: Enemy Within')
        scrape_data(conn, 'Sniper', 'https://xcom.fandom.com/wiki/Sniper_Class', 'XCOM: Enemy Unknown', 'XCOM: Enemy Within')
        scrape_data(conn, 'Support', 'https://xcom.fandom.com/wiki/Support_Class_(XCOM:_Enemy_Unknown)', 'XCOM: Enemy Unknown', 'XCOM: Enemy Within')
        scrape_data(conn, 'Ranger', 'https://xcom.fandom.com/wiki/Ranger_Class_(XCOM_2)', 'XCOM 2', 'XCOM 2: War of the Chosen')
        scrape_data(conn, 'Specialist', 'https://xcom.fandom.com/wiki/Specialist_Class_(XCOM_2)', 'XCOM 2', 'XCOM 2: War of the Chosen')
        scrape_data(conn, 'Sharpshooter', 'https://xcom.fandom.com/wiki/Sharpshooter_Class_(XCOM_2)', 'XCOM 2', 'XCOM 2: War of the Chosen')
        scrape_data(conn, 'Grenadier', 'https://xcom.fandom.com/wiki/Grenadier_Class_(XCOM_2)', 'XCOM 2', 'XCOM 2: War of the Chosen')
        add_hard_coded_classes(conn)

        # Close the connection
        conn.close()

if __name__ == '__main__':
    main()
