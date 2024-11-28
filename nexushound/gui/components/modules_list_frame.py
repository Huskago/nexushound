import customtkinter as ctk


class ModuleListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, title, modules):
        super().__init__(master, label_text=title)
        self.grid_columnconfigure(0, weight=1)
        self.modules = modules
        self.buttons = []

        for i, module in enumerate(self.modules):
            button = ctk.CTkButton(self, text=module)
            button.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.buttons.append(button)
