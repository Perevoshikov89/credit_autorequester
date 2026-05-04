import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading

from config import HOSTS
from core.processor import process_all


class AppGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Credit Autorequester")
        self.root.geometry("700x500")

        self.path = tk.StringVar()
        self.host = tk.IntVar(value=100)

        self.build_ui()

    def build_ui(self):
        # ===== ПАПКА =====
        frame_path = tk.Frame(self.root)
        frame_path.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_path, text="Папка запросов:").pack(side="left")

        tk.Entry(frame_path, textvariable=self.path, width=50).pack(side="left", padx=5)

        tk.Button(frame_path, text="Выбрать", command=self.select_folder).pack(side="left")

        # ===== HOST =====
        frame_host = tk.Frame(self.root)
        frame_host.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_host, text="Host:").pack(side="left")

        self.host_combo = ttk.Combobox(
            frame_host,
            values=list(HOSTS.keys()),
            width=10,
            state="readonly"
        )
        self.host_combo.set(100)
        self.host_combo.pack(side="left", padx=5)

        # ===== КНОПКА =====
        tk.Button(
            self.root,
            text="🚀 Запустить обработку",
            bg="green",
            fg="white",
            command=self.start_process
        ).pack(pady=10)

        # ===== ПРОГРЕСС =====
        self.progress = ttk.Progressbar(self.root, length=600, mode="indeterminate")
        self.progress.pack(pady=5)

        # ===== ЛОГ ОКНО =====
        self.log_box = scrolledtext.ScrolledText(self.root, height=18)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path.set(folder)

    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def start_process(self):
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        self.progress.start()

        try:
            path = self.path.get()
            host = int(self.host_combo.get())
            url = HOSTS.get(host)

            self.log(f"Старт обработки. Host={host}")
            self.log(f"Папка: {path}")

            process_all(path, "req_*.xml", url)

            self.log("Готово!")

        except Exception as e:
            self.log(f"Ошибка: {e}")

        self.progress.stop()


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()