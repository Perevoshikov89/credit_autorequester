import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading
import requests
import subprocess as sp
import os
import fnmatch
import vkbeautify as vkb

# ---------------- HOST ----------------
HOSTS = {
    100: "http://client.demo.nbki.msk:8082/products/B2BRUTDF",
    102: "http://client-alfa.demo.nbki.msk:8082/products/B2BRUTDF",
    103: "https://reports.test-alfa.nbki.ru/products/B2BRUTDF",
    200: "http://client.demo.nbki.msk:8082/NbchScore",
}


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("NBKI Mini Tool")
        self.root.geometry("750x500")

        self.path = tk.StringVar()
        self.host = tk.IntVar(value=100)

        self.create_ui()

    # ---------------- UI ----------------
    def create_ui(self):

        top = tk.Frame(self.root)
        top.pack(pady=10)

        # ПУТЬ
        tk.Label(top, text="Папка:").pack(side=tk.LEFT)

        tk.Entry(top, textvariable=self.path, width=40).pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="...", command=self.select_folder).pack(side=tk.LEFT)

        # HOST
        ttk.Combobox(
            top,
            textvariable=self.host,
            values=[100, 102, 103, 200],
            width=5
        ).pack(side=tk.LEFT, padx=10)

        # START
        tk.Button(top, text="СТАРТ", bg="green", fg="white",
                  command=self.start).pack(side=tk.LEFT)

        # PROGRESS
        self.progress = ttk.Progressbar(self.root, length=700)
        self.progress.pack(pady=10)

        # LOG
        self.log_box = scrolledtext.ScrolledText(self.root, height=20)
        self.log_box.pack(fill=tk.BOTH, expand=True)

    # ---------------- LOG ----------------
    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    # ---------------- SELECT FOLDER ----------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path.set(folder)

    # ---------------- START ----------------
    def start(self):
        threading.Thread(target=self.process).start()

    # ---------------- PROCESS ----------------
    def process(self):

        NBKIpath = self.path.get()
        host = self.host.get()

        if not NBKIpath:
            self.log("❌ Выбери папку")
            return

        if host not in HOSTS:
            self.log("❌ Неверный host")
            return

        url = HOSTS[host]

        os.chdir(NBKIpath)

        files = fnmatch.filter(os.listdir(NBKIpath), "req_*.xml")

        total = len(files)
        self.progress["maximum"] = total
        self.progress["value"] = 0

        self.log(f"Найдено файлов: {total}")

        for i, reqFile in enumerate(files):

            self.log(f"\nОбработка: {reqFile}")
            full_path = os.path.abspath(reqFile)

            # -------- ЭЦП --------
            try:
                cmd = f'ecp.bat "{full_path}"'

                result = sp.run(
                    cmd,
                    shell=True,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE,
                    timeout=60
                )

                self.log(result.stdout.decode(errors="ignore"))
                self.log(result.stderr.decode(errors="ignore"))

                if result.returncode != 0:
                    raise RuntimeError("Ошибка ЭЦП")

                self.log("✔ Подписано")

            except Exception as e:
                self.log(f"❌ ЭЦП ошибка: {e}")
                continue

            # -------- POST --------
            sig_file = full_path + ".sig"

            try:
                with open(sig_file, "rb") as f:
                    response = requests.post(
                        url,
                        data=f.read(),
                        headers={"Content-Type": "application/pkcs7"},
                        timeout=60
                    )

                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}")

                with open("Pyt.xml", "wb") as f:
                    f.write(response.content)

                self.log("✔ Ответ получен")

            except Exception as e:
                self.log(f"❌ Ошибка запроса: {e}")
                continue

            # -------- UNSIGN --------
            try:
                cmd = 'cp.bat "Pyt.xml"'

                result = sp.run(
                    cmd,
                    shell=True,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE,
                    timeout=60
                )

                self.log(result.stdout.decode(errors="ignore"))

                if result.returncode != 0:
                    raise RuntimeError("Ошибка снятия ЭЦП")

                self.log("✔ ЭЦП снята")

            except Exception as e:
                self.log(f"❌ Ошибка снятия: {e}")
                continue

            # -------- RESULT --------
            try:
                out_name = reqFile.replace("req_", "KO_")

                def read_xml(file):
                    for enc in ("utf-8", "cp1251", "windows-1251"):
                        try:
                            with open(file, "r", encoding=enc) as f:
                                return f.read()
                        except:
                            continue
                    raise RuntimeError("Кодировка не определена")

                xml = read_xml("des_Pyt.xml")

                formatted = vkb.xml(xml)

                with open(out_name, "w", encoding="utf-8") as f:
                    f.write(formatted)

                self.log(f"✔ Сохранено: {out_name}")

            except Exception as e:
                self.log(f"❌ Ошибка записи: {e}")

            # -------- CLEAN --------
            for f in [sig_file, "des_Pyt.xml", "Pyt.xml"]:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except:
                    pass

            self.progress["value"] = i + 1
            self.root.update_idletasks()

        self.log("\n✅ Готово")


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()