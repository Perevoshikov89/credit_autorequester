import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os

from config import NBKI_PATH, REQ_PATTERN, HOSTS
from core.file_manager import get_request_files
from core.formatter import format_xml
from core.signer import sign_file
from core.verifier import unsign_file
from core.builder import build_ko
from services.http_service import send_request
from utils.logger import setup_logger

logger = setup_logger(NBKI_PATH)


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("NBKI Processor")
        self.root.geometry("750x500")

        self.create_ui()

    def create_ui(self):

        top = tk.Frame(self.root)
        top.pack(pady=10)

        tk.Label(top, text="Host:").pack(side=tk.LEFT)

        self.host = ttk.Combobox(top, values=[100, 102, 103, 200], width=10)
        self.host.set(100)
        self.host.pack(side=tk.LEFT)

        self.start_btn = tk.Button(
            top,
            text="START",
            bg="green",
            fg="white",
            command=self.start
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.progress = ttk.Progressbar(self.root, length=700)
        self.progress.pack(pady=10)

        self.log = scrolledtext.ScrolledText(self.root, height=20)
        self.log.pack(fill=tk.BOTH, expand=True)

    def write(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        logger.info(msg)

    def start(self):
        threading.Thread(target=self.process).start()

    def process(self):

        host = int(self.host.get())
        url = HOSTS[host]

        files = get_request_files(NBKI_PATH, REQ_PATTERN)

        self.progress["maximum"] = len(files)
        self.progress["value"] = 0

        for i, file in enumerate(files):

            try:
                self.write(f"Файл: {file}")

                path = os.path.join(NBKI_PATH, file)

                with open(path, "r", encoding="utf-8") as f:
                    xml = f.read()

                xml = format_xml(xml)

                with open(path, "w", encoding="utf-8") as f:
                    f.write(xml)

                sign_file(file)

                sig = file + ".sig"

                resp = send_request(url, sig)

                with open("Pyt.xml", "wb") as f:
                    f.write(resp)

                unsign_file("Pyt.xml")

                out = file.replace("req_", "KO_")

                build_ko("des_Pyt.xml", os.path.join("output", out))

                self.write(f"ГОТОВО: {out}")

                for f in [sig, "Pyt.xml", "des_Pyt.xml"]:
                    try:
                        os.remove(f)
                    except:
                        pass

            except Exception as e:
                self.write(f"ОШИБКА: {file} -> {e}")

            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.write("ВСЁ ГОТОВО")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()