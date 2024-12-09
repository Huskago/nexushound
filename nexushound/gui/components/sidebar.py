import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, modules):
        super().__init__(master)
        self.modules = modules
        self.on_module_select = None

        self.create_category_tree()

    def create_category_tree(self):
        for category, modules in self.get_categorized_modules().items():
            category_frame = ctk.CTkFrame(self)
            category_frame.pack(fill="x", padx=5, pady=2)

            category_label = ctk.CTkLabel(category_frame, text=category)
            category_label.pack(anchor="w", padx=5)

            for module in modules:
                btn = ctk.CTkButton(
                    category_frame,
                    text=module.name,
                    command=lambda m=module: self.select_module(m)
                )
                btn.pack(fill="x", padx=5, pady=2)

    def get_categorized_modules(self):
        categories = {}
        for module in self.modules.values():
            if module.category not in categories:
                categories[module.category] = []
            categories[module.category].append(module)
        return categories

    def select_module(self, module):
        if self.on_module_select:
            self.on_module_select(module)

    def filter_modules(self, query):
        # Implement module filtering based on search query
        pass