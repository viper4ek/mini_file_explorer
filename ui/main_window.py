import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path

from core.file_system import FileSystemManager
from ui.context_menus import ContextMenuManager


class MiniFileExplorer(tk.Tk):
    FORBIDDEN_CHARS = r'\/:*?"<>|'

    def __init__(self):
        super().__init__()
        self.title("Провідник")
        self.geometry("1150x700")
        self.set_theme("dark")

        self.fs = FileSystemManager()
        self.history_back = []
        self.history_forward = []
        self.sort_column = "name"
        self.sort_reverse = False
        self.current_items = []

        self._create_widgets()
        self._init_context_menus()
        self._bind_events()
        self._load_sidebar()

        self.set_theme("dark")
        self.navigate_to(self.fs.current_path, save_history=False)

    def set_theme(self, mode="dark"):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        if mode == "dark":
            bg_color, fg_color = "#1E1E1E", "#D4D4D4"
            sel_bg_color, sel_fg_color = "#007ACC", "#FFFFFF"
            panel_bg, header_bg = "#252526", "#333333"
            btn_bg, btn_active = "#3C3C3C", "#505050"
        else:
            bg_color, fg_color = "#F3F3F3", "#000000"
            sel_bg_color, sel_fg_color = "#0078D7", "#FFFFFF"
            panel_bg, header_bg = "#FFFFFF", "#E1E1E1"
            btn_bg, btn_active = "#E1E1E1", "#D1D1D1"

        main_font = ("Segoe UI", 10)
        header_font = ("Segoe UI", 10, "bold")
        mono_font = ("Consolas", 10)

        self.configure(bg=bg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color, font=header_font)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color, font=header_font)
        style.configure("TButton", font=main_font, background=btn_bg, foreground=fg_color, borderwidth=0,
                        focusthickness=0)
        style.map("TButton", background=[("active", btn_active), ("pressed", sel_bg_color)],
                  foreground=[("active", fg_color)])
        style.configure("TMenubutton", font=main_font, background=btn_bg, foreground=fg_color, borderwidth=0)
        style.map("TMenubutton", background=[("active", btn_active)])
        style.configure("TEntry", fieldbackground=panel_bg, foreground=fg_color, font=main_font, insertcolor=fg_color,
                        borderwidth=1)
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color, font=main_font)
        style.map("TCheckbutton", background=[("active", bg_color)])
        style.configure("Treeview", background=panel_bg, foreground=fg_color, fieldbackground=panel_bg, font=main_font,
                        rowheight=26, borderwidth=0)
        style.map("Treeview", background=[("selected", sel_bg_color)], foreground=[("selected", sel_fg_color)])
        style.configure("Treeview.Heading", background=header_bg, foreground=fg_color, font=header_font, relief="flat",
                        padding=5)
        style.map("Treeview.Heading", background=[("active", btn_active)])
        style.configure("TScrollbar", background=btn_bg, troughcolor=bg_color, borderwidth=0, arrowcolor=fg_color)
        style.map("TScrollbar", background=[("active", btn_active)])
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=main_font)

        if hasattr(self, 'preview_text'):
            self.preview_text.config(
                bg=panel_bg, fg=fg_color, insertbackground=fg_color,
                selectbackground=sel_bg_color, selectforeground=sel_fg_color,
                font=mono_font, relief="flat", padx=10, pady=10
            )

    def _create_widgets(self):
        command_bar = ttk.Frame(self)
        command_bar.pack(fill=tk.X, padx=5, pady=(5, 2))

        self.btn_create = ttk.Menubutton(command_bar, text="➕ Створити")
        command_bar_create_menu = tk.Menu(self.btn_create, tearoff=0)
        command_bar_create_menu.add_command(label="📁 Папку", command=self.create_folder)
        command_bar_create_menu.add_separator()
        command_bar_create_menu.add_command(label="📝 Текстовий документ (.txt)",
                                            command=lambda: self.create_doc(".txt"))
        command_bar_create_menu.add_command(label="📄 Документ Word (.docx)", command=lambda: self.create_doc(".docx"))
        command_bar_create_menu.add_command(label="📊 Аркуш Excel (.xlsx)", command=lambda: self.create_doc(".xlsx"))
        command_bar_create_menu.add_command(label="📦 ZIP-архів (.zip)", command=lambda: self.create_doc(".zip"))
        self.btn_create["menu"] = command_bar_create_menu
        self.btn_create.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(command_bar, text="📋 Копіювати", command=self.copy_item).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(command_bar, text="✂ Вирізати", command=self.cut_item).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(command_bar, text="📋 Вставити", command=self.paste_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(command_bar, text="✏ Перейменувати", command=self.rename_item).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(command_bar, text="❌ Видалити", command=self.delete_item).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(command_bar, text="🔄 Оновити", command=lambda: self.load_directory(self.fs.current_path)).pack(
            side=tk.LEFT)

        btn_dark = ttk.Button(command_bar, text="🌙", width=3, command=lambda: self.set_theme("dark"))
        btn_dark.pack(side=tk.RIGHT, padx=(2, 5))
        btn_light = ttk.Button(command_bar, text="☀️", width=3, command=lambda: self.set_theme("light"))
        btn_light.pack(side=tk.RIGHT, padx=(0, 2))

        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        self.btn_back = ttk.Button(nav_frame, text="⬅", width=3, command=self.go_back, state=tk.DISABLED)
        self.btn_back.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_forward = ttk.Button(nav_frame, text="➡", width=3, command=self.go_forward, state=tk.DISABLED)
        self.btn_forward.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(nav_frame, text="⬆ Вгору", command=self.on_up_clicked).pack(side=tk.LEFT, padx=(0, 5))

        self.path_entry = ttk.Entry(nav_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.path_entry.bind("<Return>", self.on_path_entered)

        ttk.Label(nav_frame, text="🔍").pack(side=tk.LEFT, padx=(5, 2))
        self.search_entry = ttk.Entry(nav_frame, width=18)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)
        self.recursive_var = tk.BooleanVar(value=False)
        chk_rec = ttk.Checkbutton(nav_frame, text="У підпапках", variable=self.recursive_var,
                                  command=lambda: self.on_search_changed(None))
        chk_rec.pack(side=tk.LEFT)

        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        sidebar_frame = ttk.Frame(self.paned_window)
        self.sidebar_tree = ttk.Treeview(sidebar_frame, selectmode="browse", show="tree")
        sidebar_scroll = ttk.Scrollbar(sidebar_frame, orient=tk.VERTICAL, command=self.sidebar_tree.yview)
        self.sidebar_tree.configure(yscrollcommand=sidebar_scroll.set)
        self.sidebar_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sidebar_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.paned_window.add(sidebar_frame, weight=1)
        self.sidebar_tree.bind("<<TreeviewSelect>>", self.on_sidebar_select)

        tree_frame = ttk.Frame(self.paned_window)
        columns = ("type", "size", "modified")
        self.tree = ttk.Treeview(tree_frame, columns=columns, selectmode="extended")

        tree_scroll_v = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_h = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)

        self.tree.heading("#0", text="Ім'я ⇅", anchor=tk.W, command=lambda: self.sort_by("name"))
        self.tree.heading("type", text="Тип ⇅", anchor=tk.W, command=lambda: self.sort_by("type"))
        self.tree.heading("size", text="Розмір ⇅", anchor=tk.E, command=lambda: self.sort_by("raw_size"))
        self.tree.heading("modified", text="Дата зміни ⇅", anchor=tk.W, command=lambda: self.sort_by("raw_mtime"))
        self.tree.column("#0", width=250, stretch=False)
        self.tree.column("type", width=110, stretch=False)
        self.tree.column("size", width=85, anchor=tk.E, stretch=False)
        self.tree.column("modified", width=140, stretch=False)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_v.grid(row=0, column=1, sticky="ns")
        tree_scroll_h.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.paned_window.add(tree_frame, weight=3)

        preview_frame = ttk.LabelFrame(self.paned_window, text=" Панель прев'ю ")
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.paned_window.add(preview_frame, weight=2)
        self._setup_preview_copy_support()

        self.status_label = ttk.Label(self, text="", relief="flat", anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)

    def _is_valid_name(self, name: str) -> bool:
        if any(char in self.FORBIDDEN_CHARS for char in name):
            messagebox.showwarning("Некоректне ім'я", f"Ім'я не може містити:\n\\ / : * ? \" < > |", parent=self)
            return False
        return True

    def _setup_preview_copy_support(self):
        def block_edit(event):
            if event.state & 4:
                if event.keysym.lower() in ('c', 'a', 'insert'): return
            if event.keysym in ('Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Prior', 'Next', 'Shift_L', 'Shift_R',
                                'Control_L', 'Control_R'): return
            return "break"

        self.preview_text.bind("<Key>", block_edit)
        self.preview_context_menu = tk.Menu(self.preview_text, tearoff=0)
        self.preview_context_menu.add_command(label="📋 Скопіювати", command=self.copy_preview_selection)
        self.preview_context_menu.add_command(label="📋 Виділити все", command=self.select_all_preview)
        self.preview_text.bind("<Button-3>", lambda e: self.preview_context_menu.post(e.x_root, e.y_root))

    def copy_preview_selection(self):
        try:
            selected_text = self.preview_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            self.status_label.config(text=" Текст скопійовано в буфер обміну!")
        except tk.TclError:
            pass

    def select_all_preview(self):
        self.preview_text.tag_add(tk.SEL, "1.0", tk.END)
        self.preview_text.mark_set(tk.INSERT, "1.0")
        self.preview_text.see(tk.INSERT)

    def _init_context_menus(self):
        actions = {
            "create_folder": self.create_folder,
            "create_doc": self.create_doc,
            "refresh": lambda: self.load_directory(self.fs.current_path),
            "open_selected": self.open_selected_item,
            "copy_item": self.copy_item,
            "cut_item": self.cut_item,
            "paste_item": self.paste_item,
            "rename": self.rename_item,
            "delete": self.delete_item
        }
        self.menu_manager = ContextMenuManager(self, actions)

    def _bind_events(self):
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.bind("<Control-c>", lambda e: self.copy_item())
        self.bind("<Control-C>", lambda e: self.copy_item())
        self.bind("<Control-x>", lambda e: self.cut_item())
        self.bind("<Control-X>", lambda e: self.cut_item())
        self.bind("<Control-v>", lambda e: self.paste_item())
        self.bind("<Control-V>", lambda e: self.paste_item())
        self.bind("<Delete>", lambda e: self.delete_item())
        self.bind("<Alt-Left>", lambda e: self.go_back())
        self.bind("<Alt-Right>", lambda e: self.go_forward())

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if len(selected) == 1:
            self._update_preview(selected[0])
        else:
            self._clear_preview()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.menu_manager.show_menu(event, is_item_selected=True)
        else:
            self.tree.selection_clear()
            self.menu_manager.show_menu(event, is_item_selected=False)

    def _update_preview(self, tree_item_id):
        item_tags = self.tree.item(tree_item_id, "tags")
        if not item_tags: return
        target_path = Path(item_tags[0])
        preview_content = self.fs.get_file_preview(target_path)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, preview_content)

    def _clear_preview(self):
        self.preview_text.delete("1.0", tk.END)

    def sort_by(self, column_key: str):
        if self.sort_column == column_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_key
            self.sort_reverse = False
        if column_key in ("raw_size", "raw_mtime"):
            self.current_items.sort(key=lambda x: (not x["is_dir"], x[column_key]), reverse=self.sort_reverse)
        else:
            self.current_items.sort(key=lambda x: (not x["is_dir"], str(x[column_key]).lower()),
                                    reverse=self.sort_reverse)
        self._populate_tree(self.current_items)

    def navigate_to(self, target_path: Path, save_history: bool = True):
        if save_history and self.fs.current_path != target_path:
            self.history_back.append(self.fs.current_path)
            self.history_forward.clear()
        self.load_directory(target_path)
        self._update_nav_buttons()

    def go_back(self):
        if self.history_back:
            prev_path = self.history_back.pop()
            self.history_forward.append(self.fs.current_path)
            self.load_directory(prev_path)
            self._update_nav_buttons()

    def go_forward(self):
        if self.history_forward:
            next_path = self.history_forward.pop()
            self.history_back.append(self.fs.current_path)
            self.load_directory(next_path)
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        self.btn_back.config(state=tk.NORMAL if self.history_back else tk.DISABLED)
        self.btn_forward.config(state=tk.NORMAL if self.history_forward else tk.DISABLED)

    def _load_sidebar(self):
        quick_items = self.fs.get_quick_access()
        for label, path in quick_items:
            node_id = self.sidebar_tree.insert("", tk.END, text=f" {label}")
            self.sidebar_tree.item(node_id, tags=(str(path),))

    def load_directory(self, path: Path):
        try:
            items = self.fs.get_items(path)
            self.fs.current_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, str(path))
            self.search_entry.delete(0, tk.END)
            self._clear_preview()
            self.current_items = items
            self._populate_tree(items)
        except Exception as e:
            messagebox.showerror("Помилка доступу", str(e))

    def _populate_tree(self, items):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for item in items:
            icon = "📁 " if item["is_dir"] else "📄 "
            node_id = self.tree.insert(
                "", tk.END,
                text=icon + item["name"],
                values=(item["type"], item["size"], item["modified"])
            )
            self.tree.item(node_id, tags=(str(item["path"]),))

        self.status_label.config(text=f" Елементів у папці: {len(items)}")

    def on_sidebar_select(self, event):
        selected = self.sidebar_tree.selection()
        if selected:
            path_str = self.sidebar_tree.item(selected[0], "tags")[0]
            self.navigate_to(Path(path_str))

    def on_up_clicked(self):
        new_path = self.fs.current_path.parent
        if new_path != self.fs.current_path:
            self.navigate_to(new_path)

    def on_path_entered(self, event):
        entered_path = Path(self.path_entry.get().strip())
        if entered_path.exists() and entered_path.is_dir():
            self.navigate_to(entered_path)
        else:
            messagebox.showwarning("Увага", "Вказаний шлях не існує")

    def on_search_changed(self, event):
        query = self.search_entry.get().strip()
        is_rec = self.recursive_var.get()
        filtered = self.fs.search_items(query, self.fs.current_path, recursive=is_rec)
        self.current_items = filtered
        self._populate_tree(filtered)

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item: return
        target_path = Path(self.tree.item(item, "tags")[0])
        if target_path.is_dir():
            self.navigate_to(target_path)
        else:
            try:
                self.fs.open_file(target_path)
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")

    def open_selected_item(self):
        selected = self.tree.selection()
        if len(selected) != 1:
            messagebox.showinfo("Інформація", "Оберіть рівно один об'єкт для відкриття.")
            return

        target_path = Path(self.tree.item(selected[0], "tags")[0])
        if target_path.is_dir():
            self.navigate_to(target_path)
        else:
            self.fs.open_file(target_path)

    def copy_item(self):
        selected = self.tree.selection()
        if not selected: return
        paths = [Path(self.tree.item(item, "tags")[0]) for item in selected]
        self.fs.set_clipboard(paths, "copy")
        self.status_label.config(text=f" Скопійовано об'єктів у буфер: {len(paths)}")

    def cut_item(self):
        selected = self.tree.selection()
        if not selected: return
        paths = [Path(self.tree.item(item, "tags")[0]) for item in selected]
        self.fs.set_clipboard(paths, "cut")
        self.status_label.config(text=f" Вирізано об'єктів у буфер: {len(paths)}")

    def paste_item(self):
        try:
            self.fs.paste_clipboard()
            self.load_directory(self.fs.current_path)
            self.status_label.config(text=" Об'єкти успішно вставлено!")
        except Exception as e:
            messagebox.showerror("Помилка буфера", str(e))

    def create_folder(self):
        name = simpledialog.askstring("Нова папка", "Введіть назву папки:", parent=self)
        if name:
            if not self._is_valid_name(name): return
            try:
                self.fs.create_folder(name)
                self.load_directory(self.fs.current_path)
            except Exception as e:
                messagebox.showerror("Помилка доступу", str(e))

    def create_doc(self, ext: str):
        name = simpledialog.askstring("Створити документ", f"Введіть назву файлу ({ext}):", parent=self)
        if name:
            if not self._is_valid_name(name): return
            try:
                self.fs.create_document(name, ext)
                self.load_directory(self.fs.current_path)
            except Exception as e:
                messagebox.showerror("Помилка доступу", str(e))

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Інформація", "Оберіть файл або папку для видалення")
            return

        if messagebox.askyesno("Підтвердження видалення", f"Ви дійсно хочете видалити {len(selected)} об'єкт(ів)?",
                               parent=self):
            for item in selected:
                target_path = Path(self.tree.item(item, "tags")[0])
                try:
                    self.fs.delete_item(target_path)
                except Exception as e:
                    messagebox.showerror("Помилка доступу", f"Не вдалося видалити {target_path.name}:\n{e}")
            self.load_directory(self.fs.current_path)

    def rename_item(self):
        selected = self.tree.selection()
        if len(selected) != 1:
            messagebox.showinfo("Інформація", "Оберіть РІВНО ОДИН об'єкт для перейменування")
            return

        target_path = Path(self.tree.item(selected[0], "tags")[0])
        new_name = simpledialog.askstring("Перейменування", "Нова назва:", initialvalue=target_path.name, parent=self)
        if new_name and new_name != target_path.name:
            if not self._is_valid_name(new_name): return
            if not target_path.is_dir():
                old_ext, new_ext = target_path.suffix.lower(), Path(new_name).suffix.lower()
                if old_ext != new_ext:
                    if not messagebox.askyesno("Зміна розширення",
                                               f"Якщо змінити розширення, файл може стати непридатним.\nВи дійсно бажаєте змінити його?",
                                               parent=self):
                        return
            try:
                self.fs.rename_item(target_path, new_name)
                self.load_directory(self.fs.current_path)
            except Exception as e:
                messagebox.showerror("Помилка доступу", str(e))