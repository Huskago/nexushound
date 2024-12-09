import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, modules):
        super().__init__(master)
        self.modules = list(modules.values())
        self.all_modules = self.modules.copy()
        self.on_module_select = None
        self.category_frames = {}
        self.module_buttons = {}
        self.create_category_tree()

    def create_category_tree(self):
        self.clear_tree()
        categories = self.get_categorized_modules()

        for category, modules in categories.items():
            category_frame = ctk.CTkFrame(self)
            category_frame.pack(fill="x", padx=5, pady=2)

            category_label = ctk.CTkLabel(category_frame, text=category)
            category_label.pack(anchor="w", padx=5)

            for module in modules:
                btn = ctk.CTkButton(
                    category_frame,
                    text=module.name,
                    command=lambda m=module: self.select_module(m),
                    fg_color="red" if module.is_modified else None
                )
                self.create_tooltip(btn, "Module source code has been modified!" if module.is_modified else None)
                btn.pack(fill="x", padx=5, pady=2)

    def create_tooltip(self, widget, text):
        if not text:
            return

        tooltip = ctk.CTkFrame(self)
        tooltip_label = ctk.CTkLabel(tooltip, text=text)
        tooltip_label.pack(padx=5, pady=2)

        def show_tooltip(event):
            tooltip.place(x=event.x_root, y=event.y_root)

        def hide_tooltip(event):
            tooltip.place_forget()

        widget.bind('<Enter>', show_tooltip)
        tooltip.bind('<Leave>', hide_tooltip)

    def clear_tree(self):
        for frame in self.winfo_children():
            frame.destroy()
        self.category_frames.clear()
        self.module_buttons.clear()

    def get_categorized_modules(self):
        categories = {}
        for module in self.modules:
            if module.category not in categories:
                categories[module.category] = []
            categories[module.category].append(module)
        return categories

    def select_module(self, module):
        if self.on_module_select:
            self.on_module_select(module)

    def filter_modules(self, query):
        query = query.strip().lower()
        filtered_modules = []

        if query.startswith('#'):
            # Search only tags
            tag_query = query[1:]
            filtered_modules = [
                module for module in self.all_modules
                if any(tag_query in tag.lower() for tag in module.tags)
            ]
        else:
            # Search everything
            filtered_modules = [
                module for module in self.all_modules
                if (query in module.name.lower() or
                    query in module.description.lower() or
                    query in module.category.lower() or
                    any(query in tag.lower() for tag in module.tags))
            ]

        self.modules = filtered_modules
        self.create_category_tree()