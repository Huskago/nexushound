from nexushound.database.manager import DatabaseManager
from nexushound.gui.app import App

def main():
    db = DatabaseManager()
    app = App()
    app.mainloop()
    db.close()