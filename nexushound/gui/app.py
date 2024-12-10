import customtkinter as ctk

from nexushound.gui.components.module_view import ModuleView
from nexushound.gui.components.search_bar import SearchBar
from nexushound.gui.components.sidebar import Sidebar
from nexushound.modules_manager import ModuleLoader


class App(ctk.CTk):
    def __init__(self, db=None):
        super().__init__()

        self.title("NexusHound")
        self.geometry("1200x800")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Initialize module loader and database
        self.db = db
        self.loader = ModuleLoader()
        self.modules = self.loader.load_all_modules()

        # Create search bar
        self.search_bar = SearchBar(self)
        self.search_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Create sidebar with categories
        self.sidebar = Sidebar(self, self.modules)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create main module view
        self.module_view = ModuleView(self)
        self.module_view.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Bind events
        self.sidebar.on_module_select = self.module_view.display_module
        self.search_bar.on_search = self.sidebar.filter_modules