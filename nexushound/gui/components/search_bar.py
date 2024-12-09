import customtkinter as ctk

class SearchBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.on_search = None

        self.entry = ctk.CTkEntry(self, placeholder_text="Search modules...")
        self.entry.pack(side="left", fill="x", expand=True, padx=5)
        self.entry.bind("<KeyRelease>", self.search)

    def search(self, event):
        if self.on_search:
            self.on_search(self.entry.get())