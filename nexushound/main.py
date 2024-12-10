from nexushound.database.manager import DatabaseManager
from nexushound.gui.app import App

def main():
    try:
        db = DatabaseManager()
        db.init_db()
        db.add_default_wordlists()

        app = App(db=db)
        app.mainloop()

    except Exception as e:
        print(f"Error starting application: {e}")
        raise
    finally:
        if 'db' in locals():
            db.close()

if __name__ == '__main__':
    main()