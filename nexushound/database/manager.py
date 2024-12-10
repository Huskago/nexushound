import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "nexushound/nexushound.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize the database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r') as f:
            schema = f.read()

        self.conn = sqlite3.connect(self.db_path)
        self.conn.executescript(schema)
        self.conn.commit()

    def get_module_hash(self, module_path: Path) -> str:
        """Calculate SHA-256 hash of module file"""
        with open(module_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def register_module(self, module_data: Dict[str, Any], module_path: Path) -> int:
        """Register a module in the database"""

        # Verify if module exist already
        try:
            query = "SELECT id_mod, module_hash FROM MODULE WHERE name = ? AND category = ?"
            cursor = self.conn.execute(query, (module_data.get('name'), module_data.get('category')))
            row = cursor.fetchone()

            current_hash = self.get_module_hash(module_path)

            if row:
                if current_hash != row[1]:
                    print(f"Warning: Module {module_data.get('name')} has been modified")
                return row[0]

            query = """
                INSERT INTO MODULE (name, category, description, version,
                                    authors, dependencies, module_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            authors = json.dumps(module_data.get('authors', []))
            dependencies = json.dumps(module_data.get('dependencies', []))
            module_hash = self.get_module_hash(module_path)

            values = (
                module_data.get('name'),
                module_data.get('category'),
                module_data.get('description'),
                module_data.get('version'),
                authors,
                dependencies,
                module_hash
            )

            cursor = self.conn.execute(query, values)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return -1

    def verify_module(self, module_id: int, module_path: Path) -> bool:
        """Verify module integrity using stored hash"""
        query = "SELECT module_hash FROM MODULE WHERE id_mod = ?"
        cursor = self.conn.execute(query, (module_id,))
        row = cursor.fetchone()

        if row:
            stored_hash = row[0]
            current_hash = self.get_module_hash(module_path)
            return stored_hash == current_hash
        return False

    def add_wordlist(self, name: str, elements: List[str]) -> int:
        """Add a new wordlist to the database"""
        query = "INSERT INTO WORDLIST (name, elements, nb_elements) VALUES (?, ?, ?)"
        elements_json = json.dumps(elements)
        values = (name, elements_json, len(elements))

        cursor = self.conn.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid

    def add_default_wordlists(self):
        default_wordlists = {
            'big': 'nexushound/wordlists/big.txt'
        }

        for name, path in default_wordlists.items():
            if Path(path).exists():
                query = "SELECT id_wordlist FROM WORDLIST WHERE name = ?"
                cursor = self.conn.execute(query, (name,))
                if not cursor.fetchone():
                    try:
                        encodings = ['utf-8', 'latin-1', 'ascii', 'utf-16']

                        for encoding in encodings:
                            try:
                                with open(path, 'r', encoding=encoding) as f:
                                    elements = [line.strip() for line in f if line.strip()]
                                self.add_wordlist(name, elements)
                                print(f"Added default wordlist: {name}")
                                break
                            except UnicodeDecodeError:
                                continue
                    except Exception as e:
                        print(f"Error loading wordlist {name}: {e}")

    def get_wordlist(self, wordlist_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a wordlist by ID"""
        query = "SELECT * FROM WORDLIST WHERE id_wordlist = ?"
        cursor = self.conn.execute(query, (wordlist_id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'elements': json.loads(row[2]),
                'nb_elements': row[3],
                'last_updated': row[4]
            }
        return None

    def get_wordlists(self) -> List[Dict[str, Any]]:
        query = "SELECT id_wordlist, name FROM WORDLIST"
        cursor = self.conn.execute(query)
        return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def save_result(self, module_id: int, results_path: str, options: Dict[str, Any]) -> int:
        """Save module execution results"""
        query = "INSERT INTO RESULT (id_mod, file_results, options) VALUES (?, ?, ?)"
        options_json = json.dumps(options)
        values = (module_id, str(results_path), options_json)

        cursor = self.conn.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid

    def get_results(self, module_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve results, optionally filtered by module ID"""
        if module_id:
            query = "SELECT * FROM RESULT WHERE id_mod = ? ORDER BY date DESC"
            cursor = self.conn.execute(query, (module_id,))
        else:
            query = "SELECT * FROM RESULT ORDER BY date DESC"
            cursor = self.conn.execute(query)

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'module_id': row[1],
                'file_path': row[2],
                'date': row[3],
                'options': json.loads(row[4]),
            })
        return results

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
