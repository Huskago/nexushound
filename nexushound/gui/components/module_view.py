import customtkinter as ctk
from pathlib import Path

from nexushound.modules_manager import WordlistOption


class ModuleView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.current_module = None
        self.create_widgets()

    def create_widgets(self):
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.pack(fill="x", padx=10, pady=5)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        self.custom_ui_frame = ctk.CTkFrame(self)
        self.custom_ui_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.run_button = ctk.CTkButton(
            self,
            text="Run Module",
            command=self.run_module
        )
        self.run_button.pack(pady=10)

    def display_module(self, module):
        self.current_module = module
        self.update_details()
        self.update_options()
        self.update_custom_ui()

    def update_details(self):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        if self.current_module:
            if self.current_module.is_modified:
                warning_frame = ctk.CTkFrame(self.details_frame, fg_color="red")
                warning_frame.pack(fill="x", padx=5, pady=5)

                warning_label = ctk.CTkLabel(
                    warning_frame,
                    text="⚠️Warning: Module source code has been modified!",
                    text_color="white"
                )
                warning_label.pack(pady=5)

            ctk.CTkLabel(self.details_frame, text=f"Name: {self.current_module.name}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Version: {self.current_module.version}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Description: {self.current_module.description}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Authors: {', '.join(self.current_module.authors)}").pack(anchor="w")

    def update_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        if self.current_module and self.current_module.options:
            ctk.CTkLabel(self.options_frame, text="Options:").pack(anchor="w")
            for option in self.current_module.options:
                self.create_option_widget(option)

    def create_option_widget(self, option):
        frame = ctk.CTkFrame(self.options_frame)
        frame.pack(fill="x", pady=2)

        ctk.CTkLabel(frame, text=option.name).pack(side="left", padx=5)

        if isinstance(option, WordlistOption):
            wordlists = self.master.loader.db.get_wordlists()
            choices = ['Custom'] + [f"{w['name']} ({w['id']})" for w in wordlists]

            combo = ctk.CTkOptionMenu(frame, values=choices)
            combo.pack(side="right", padx=5)

            entry = ctk.CTkEntry(frame, placeholder_text="Custom wordlist path")

            def on_select(choice):
                if choice == 'Custom':
                    entry.pack(side="right", padx=5)
                    option.custom_path = None
                else:
                    entry.pack_forget()
                    option.custom_path = None
                    wordlist_id = int(choice.split('(')[-1].strip(')'))
                    option.default = wordlist_id

            combo.configure(command=on_select)
            combo.set(choices[0])

        elif option.type == "choice" and option.choices:
            widget = ctk.CTkOptionMenu(frame, values=option.choices)
            widget.pack(side="right", padx=5)
        elif option.type == "bool":
            widget = ctk.CTkCheckBox(frame, text="")
            widget.pack(side="right", padx=5)
        else:
            widget = ctk.CTkEntry(frame)
            widget.pack(side="right", padx=5)

    def update_custom_ui(self):
        for widget in self.custom_ui_frame.winfo_children():
            widget.destroy()

        if self.current_module:
            self.current_module.create_ui(self.custom_ui_frame)

    def run_module(self):
        if not self.current_module:
            return

        if self.current_module.is_modified:
            dialog = ctk.CTkInputDialog(
                title="Warning",
                text="This module has been modified. Are you sure you want to run it? (yes/no)"
            )
            if dialog.get_input().lower() != "yes":
                return

        self.current_module.run()