import customtkinter as ctk

from nexushound.gui.components.modules_list_frame import ModuleListFrame
from nexushound.modules_manager import ModuleLoader


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NexusHound")
        self.geometry("400x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        loader = ModuleLoader()

        self.modules = loader.load_all_modules()

        print(self.modules)

        self.modules_list_frame = ModuleListFrame(self, "Test", self.modules)
        self.modules_list_frame.grid(row=0, column=0, padx=0, pady=0)
