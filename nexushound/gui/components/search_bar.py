import customtkinter as ctk

class SearchBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.on_search = None

        self.entry = ctk.CTkEntry(self, placeholder_text="Search modules...")
        self.entry.pack(side="left", fill="x", expand=True, padx=5)

        def select_all(event):
            event.widget.select_range(0, "end")
            return "break"

        self.entry.bind("<KeyRelease>", self.search)
        self.entry.bind("<Control-a>", select_all)


    def search(self, event):
        if self.on_search:
            self.on_search(self.entry.get())