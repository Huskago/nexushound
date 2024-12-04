import sqlite3

import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS MODULE (
            ID_mod INTEGER PRIMARY KEY,
            categorie TEXT,
            auteur TEXT,
            description TEXT,
            version TEXT,
            dependances TEXT
        );

        CREATE TABLE IF NOT EXISTS WORDLIST (
            ID_wordlist INTEGER PRIMARY KEY,
            elements TEXT,
            nb_elements INTEGER
        );

        CREATE TABLE IF NOT EXISTS RESULTAT (
            ID_elem INTEGER PRIMARY KEY,
            ID_mod INTEGER,
            file_results TEXT,
            date TEXT,
            options TEXT,
            FOREIGN KEY (ID_mod) REFERENCES MODULE (ID_mod)
        );

        CREATE TABLE IF NOT EXISTS CHOISIR (
            ID_mod INTEGER,
            ID_wordlist INTEGER,
            PRIMARY KEY (ID_mod, ID_wordlist),
            FOREIGN KEY (ID_mod) REFERENCES MODULE (ID_mod),
            FOREIGN KEY (ID_wordlist) REFERENCES WORDLIST (ID_wordlist)
        );

        CREATE TABLE IF NOT EXISTS AFFICHER (
            elem_in_file_results INTEGER PRIMARY KEY
        );
    ''')

    conn.commit()
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # c'est un exemple d'ajout d'element dans une table
    cursor.execute('''
        INSERT OR IGNORE INTO MODULE (ID_mod, categorie, auteur, description, version, dependances)
        VALUES (1, "Category1", "Author1", "Description1", "1.0", "Dependency1")
    ''')

    

    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    for table in ["MODULE", "WORDLIST", "RESULTAT", "CHOISIR"]:
        cursor.execute(f"SELECT * FROM {table}")
        print(f"{table}:", cursor.fetchall())

    conn.close()

if __name__ == "__main__":
    create_database()
    insert_sample_data()
    fetch_data()

