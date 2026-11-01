import os
import shutil
import platform
import zipfile
from pathlib import Path
from datetime import datetime


class FileSystemManager:
    def __init__(self):
        self.current_path = Path.home()
        # Змінено: тепер зберігаємо список шляхів
        self.clipboard_paths = []
        self.clipboard_action = None

    def get_items(self, path: Path = None):
        target_path = path if path else self.current_path

        if not target_path.exists() or not target_path.is_dir():
            raise ValueError("Вказаний шлях не існує або не є папкою")

        try:
            dir_contents = list(target_path.iterdir())
        except PermissionError:
            raise PermissionError(f"Відмовлено в доступі до папки:\n{target_path}")

        items = []
        for item in dir_contents:
            try:
                stats = item.stat()
                is_dir = item.is_dir()
                size = "-" if is_dir else self._format_size(stats.st_size)
                mod_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")

                items.append({
                    "name": item.name,
                    "path": item,
                    "is_dir": is_dir,
                    "type": "Папка файлів" if is_dir else f"Файл {item.suffix.upper()}",
                    "size": size,
                    "raw_size": -1 if is_dir else stats.st_size,
                    "modified": mod_time,
                    "raw_mtime": stats.st_mtime
                })
            except (PermissionError, OSError):
                continue

        return sorted(items, key=lambda x: (not x["is_dir"], x["name"].lower()))

    def search_items(self, query: str, root_path: Path = None, recursive: bool = False):
        target_path = root_path if root_path else self.current_path
        query = query.lower().strip()

        if not query:
            return self.get_items(target_path)

        if not recursive:
            all_items = self.get_items(target_path)
            return [item for item in all_items if query in item["name"].lower()]

        results = []
        count = 0
        max_results = 200

        for root, dirs, files in os.walk(target_path):
            if count >= max_results:
                break
            for name in dirs + files:
                if query in name.lower():
                    item_path = Path(root) / name
                    try:
                        stats = item_path.stat()
                        is_dir = item_path.is_dir()
                        size = "-" if is_dir else self._format_size(stats.st_size)
                        mod_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")

                        rel_path = str(item_path.relative_to(target_path))
                        results.append({
                            "name": rel_path,
                            "path": item_path,
                            "is_dir": is_dir,
                            "type": "Папка файлів" if is_dir else f"Файл {item_path.suffix.upper()}",
                            "size": size,
                            "raw_size": -1 if is_dir else stats.st_size,
                            "modified": mod_time,
                            "raw_mtime": stats.st_mtime
                        })
                        count += 1
                        if count >= max_results:
                            break
                    except (PermissionError, OSError):
                        continue
        return results

    def set_clipboard(self, paths: list, action: str):
        """Зберігає список файлів для копіювання ("copy") або вирізання ("cut")."""
        self.clipboard_paths = paths
        self.clipboard_action = action

    def paste_clipboard(self, target_dir: Path = None):
        """Вставляє всі елементи з буфера обміну."""
        if not self.clipboard_paths:
            raise ValueError("Буфер обміну порожній.")

        dst_dir = target_dir if target_dir else self.current_path

        for clip_path in self.clipboard_paths:
            if not clip_path.exists():
                continue

            dst_path = dst_dir / clip_path.name
            if dst_path.exists() and dst_path != clip_path:
                stem = clip_path.stem
                suffix = clip_path.suffix
                dst_path = dst_dir / f"{stem}_copy{suffix}"

            try:
                if self.clipboard_action == "copy":
                    if clip_path.is_dir():
                        shutil.copytree(clip_path, dst_path)
                    else:
                        shutil.copy2(clip_path, dst_path)
                elif self.clipboard_action == "cut":
                    if clip_path.parent != dst_dir:
                        shutil.move(str(clip_path), str(dst_path))
            except PermissionError:
                raise PermissionError(f"Немає прав доступу для {clip_path.name}.")

        if self.clipboard_action == "cut":
            self.clipboard_paths = []
            self.clipboard_action = None

    def get_file_preview(self, path: Path, max_bytes: int = 15000) -> str:
        if not path.exists():
            return "Об'єкт не існує."
        if path.is_dir():
            return f"📁 Папка: {path.name}\nШлях: {path}"
        if path.stat().st_size > 2 * 1024 * 1024:
            return f"📄 Файл занадто великий для прев'ю ({self._format_size(path.stat().st_size)})."

        text_exts = {'.txt', '.py', '.json', '.xml', '.html', '.css', '.js', '.md', '.log', '.csv', '.ini', '.cfg',
                     '.yaml', '.yml', '.cpp', '.h', '.c', '.cs'}
        if path.suffix.lower() not in text_exts and path.suffix != "":
            return f"📄 Файл {path.suffix.upper()}\nПрев'ю доступне для текстових файлів та коду."

        try:
            with open(path, 'rb') as f:
                raw_data = f.read(max_bytes)
            for enc in ['utf-8', 'cp1251', 'latin-1']:
                try:
                    text = raw_data.decode(enc)
                    if len(raw_data) == max_bytes:
                        text += "\n\n... [Відображено перші 15 КБ] ..."
                    return text
                except UnicodeDecodeError:
                    continue
            return "Неможливо відобразити файл у текстовому форматі."
        except Exception as e:
            return f"Не вдалося прочитати файл:\n{e}"

    def open_file(self, path: Path):
        if platform.system() == "Windows":
            os.startfile(str(path))
        elif platform.system() == "Darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')

    def get_quick_access(self):
        user_home = Path.home()
        quick_list = [
            ("🖥 Робочий стіл", user_home / "Desktop"),
            ("📁 Документи", user_home / "Documents"),
            ("📥 Завантаження", user_home / "Downloads"),
            ("🖼 Зображення", user_home / "Pictures"),
            ("🎵 Музика", user_home / "Music"),
            ("🎬 Відео", user_home / "Videos"),
        ]

        if platform.system() == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = Path(f"{letter}:/")
                if drive.exists():
                    quick_list.append((f"💾 Локальний диск ({letter}:)", drive))
        return [q for q in quick_list if q[1].exists()]

    def create_folder(self, folder_name: str):
        try:
            new_path = self.current_path / folder_name
            new_path.mkdir(exist_ok=False)
        except PermissionError:
            raise PermissionError("Немає прав доступу для створення папки.")

    def create_document(self, name: str, extension: str):
        try:
            if not name.endswith(extension):
                name += extension
            new_path = self.current_path / name

            if extension == ".zip":
                with zipfile.ZipFile(new_path, 'w') as zf:
                    pass
            else:
                new_path.touch(exist_ok=False)
        except PermissionError:
            raise PermissionError("Немає прав доступу для створення файлу.")

    def delete_item(self, path: Path):
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except PermissionError:
            raise PermissionError("Немає прав для видалення.")

    def rename_item(self, old_path: Path, new_name: str):
        try:
            new_path = old_path.parent / new_name
            old_path.rename(new_path)
        except PermissionError:
            raise PermissionError("Немає прав для перейменування.")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024.0: return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} ТБ"