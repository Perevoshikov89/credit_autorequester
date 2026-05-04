from config import NBKI_PATH, HOSTS
from core.processor import process_all
from gui.app import AppGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    host = 100
    mask = "req_*.xml"

    url = HOSTS.get(host)

    if not url:
        print("Неизвестный хост")
        exit(1)

    process_all(NBKI_PATH, mask, url)