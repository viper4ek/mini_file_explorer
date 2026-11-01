import tkinter as tk

class ContextMenuManager:
    def __init__(self, parent_window, app_actions):
        self.parent = parent_window
        self.actions = app_actions
        self._create_menus()

    def _create_menus(self):
        # Вкладене меню "Створити"
        self.create_submenu = tk.Menu(self.parent, tearoff=0)
        self.create_submenu.add_command(label="📁 Папку", command=self.actions["create_folder"])
        self.create_submenu.add_separator()
        self.create_submenu.add_command(label="📝 Текстовий документ (.txt)", command=lambda: self.actions["create_doc"](".txt"))
        self.create_submenu.add_command(label="📄 Документ Word (.docx)", command=lambda: self.actions["create_doc"](".docx"))
        self.create_submenu.add_command(label="📊 Аркуш Excel (.xlsx)", command=lambda: self.actions["create_doc"](".xlsx"))
        self.create_submenu.add_command(label="📊 Презентація PowerPoint (.pptx)", command=lambda: self.actions["create_doc"](".pptx"))
        self.create_submenu.add_command(label="📦 ZIP-архів (.zip)", command=lambda: self.actions["create_doc"](".zip"))
        self.create_submenu.add_command(label="🌐 HTML документ (.html)", command=lambda: self.actions["create_doc"](".html"))
        self.create_submenu.add_command(label="🐍 Python скрипт (.py)", command=lambda: self.actions["create_doc"](".py"))

        # Меню порожнього місця (Фону)
        self.bg_context_menu = tk.Menu(self.parent, tearoff=0)
        self.bg_context_menu.add_cascade(label="➕ Створити", menu=self.create_submenu)
        self.bg_context_menu.add_command(label="📋 Вставити", command=self.actions["paste_item"])
        self.bg_context_menu.add_separator()
        self.bg_context_menu.add_command(label="🔄 Оновити", command=self.actions["refresh"])

        # Меню файлу/папки
        self.file_context_menu = tk.Menu(self.parent, tearoff=0)
        self.file_context_menu.add_command(label="📂 Відкрити", command=self.actions["open_selected"])
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="📋 Копіювати", command=self.actions["copy_item"])
        self.file_context_menu.add_command(label="✂ Вирізати", command=self.actions["cut_item"])
        self.file_context_menu.add_command(label="📋 Вставити", command=self.actions["paste_item"])
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="✏ Перейменувати", command=self.actions["rename"])
        self.file_context_menu.add_command(label="❌ Видалити", command=self.actions["delete"])

    def show_menu(self, event, is_item_selected: bool):
        if is_item_selected:
            self.file_context_menu.post(event.x_root, event.y_root)
        else:
            self.bg_context_menu.post(event.x_root, event.y_root)