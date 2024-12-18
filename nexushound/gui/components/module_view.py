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
                warning_label.pack(side="left", padx=5, pady=5)

                update_btn = ctk.CTkButton(
                    warning_frame,
                    text="Update Hash",
                    command=self.update_module_hash,
                    width=100
                )
                update_btn.pack(side="right", padx=5, pady=5)

            ctk.CTkLabel(self.details_frame, text=f"Name: {self.current_module.name}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Version: {self.current_module.version}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Description: {self.current_module.description}").pack(anchor="w")
            ctk.CTkLabel(self.details_frame, text=f"Authors: {', '.join(self.current_module.authors)}").pack(anchor="w")

    def update_module_hash(self):
        if not self.current_module or not hasattr(self.current_module, 'id'):
            return

        dialog = ctk.CTkInputDialog(
            title="Confirm Update",
            text="Are you sure you want to update the module hash? This will mark the current code as trusted. (yes/no)"
        )

        if dialog.get_input().lower() == "yes":
            module_path = self.master.loader.module_paths.get(self.current_module.name)
            if module_path:
                new_hash = self.master.loader.db.get_module_hash(Path(module_path))
                self.master.loader.db.conn.execute(
                    "UPDATE MODULE SET module_hash = ? WHERE id_mod = ?",
                    (new_hash, self.current_module.id)
                )
                self.master.loader.db.conn.commit()
                self.current_module.is_modified = False
                self.update_details()
                self.master.sidebar.refresh_module_buttons()

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

            def select_all(event):
                event.widget.select_range(0, "end")
                return "break"

            entry.bind('<Control-a>', select_all)
            entry.pack(side="right", padx=5)

            def on_select(choice):
                if choice == 'Custom':
                    entry.pack(side="right", padx=5)
                    self.current_module._option_values[option.name] = None
                else:
                    entry.pack_forget()
                    try:
                        wordlist_id = int(choice.split('(')[1].split(')')[0])
                        self.current_module._option_values[option.name] = wordlist_id
                    except:
                        print(f"Error parsing wordlist choice: {choice}")

            combo.configure(command=on_select)
            combo.set(choices[0])

        elif option.type == "choice" and option.choices:
            widget = ctk.CTkOptionMenu(frame, values=option.choices)
            def on_select(choice):
                self.current_module._option_values[option.name] = choice
            widget.configure(command=on_select)
            widget.pack(side="right", padx=5)

        elif option.type == "bool":
            widget = ctk.CTkCheckBox(frame, text="")
            def on_toggle():
                self.current_module._option_values[option.name] = widget.get()
            widget.configure(command=on_toggle)
            widget.pack(side="right", padx=5)

        elif option.type == "str":
            widget = ctk.CTkEntry(frame)
            widget.insert(0, option.default)
            widget.pack(side="right", padx=5)

            def select_all(event):
                event.widget.select_range(0, "end")
                return "break"

            def on_change(event):
                self.current_module._option_values[option.name] = widget.get()

            widget.bind('<KeyRelease>', on_change)
            widget.bind('<Control-a>', select_all)

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