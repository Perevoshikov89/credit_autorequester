import requests
import subprocess as sp
import os
import fnmatch
import vkbeautify as vkb

NBKIpath = r"E:\НБКИ\Запросы"
os.chdir(NBKIpath)

reqName = "req_*.xml"
host = 100

# ---------------- URL ----------------
HOSTS = {
    100: "http://client.demo.nbki.msk:8082/products/B2BRUTDF",
    102: "http://client-alfa.demo.nbki.msk:8082/products/B2BRUTDF",
    103: "https://reports.test-alfa.nbki.ru/products/B2BRUTDF",
    200: "http://client.demo.nbki.msk:8082/NbchScore",
}

if host not in HOSTS:
    raise ValueError(f"Хост неизвестен: {host}")

url = HOSTS[host]

# ---------------- файлы ----------------
sps = fnmatch.filter(os.listdir(NBKIpath), reqName)
count = 0

for reqFile in sps:
    print(f"\nОбработка файла: {reqFile}")

    full_path = os.path.abspath(reqFile)

    # -------- ЭЦП подпись --------
    try:
        cmd = f'ecp.bat "{full_path}"'

        result = sp.run(
            cmd,
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            timeout=60
        )

        print("STDOUT:", result.stdout.decode(errors="ignore"))
        print("STDERR:", result.stderr.decode(errors="ignore"))

        if result.returncode != 0:
            raise RuntimeError("Ошибка подписи ЭЦП")

        print("Файл подписан ЭЦП")

    except Exception as e:
        print(f"Ошибка подписи ЭЦП: {e}")
        continue

    # -------- отправка --------
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
            raise RuntimeError(f"HTTP ошибка: {response.status_code}")

        print("Ответ хоста получен")

        with open("Pyt.xml", "wb") as out:
            out.write(response.content)

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        continue

    # -------- снятие ЭЦП --------
    try:
        cmd = 'cp.bat "Pyt.xml"'

        result = sp.run(
            cmd,
            shell=True,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            timeout=60
        )

        print("STDOUT:", result.stdout.decode(errors="ignore"))
        print("STDERR:", result.stderr.decode(errors="ignore"))

        if result.returncode != 0:
            raise RuntimeError("Ошибка снятия ЭЦП")

        print("ЭЦП снята")

    except Exception as e:
        print(f"Ошибка снятия ЭЦП: {e}")
        continue

    # -------- сохранение результата --------
    try:
        out_name = reqFile.replace("req_", "KO_")

        def read_xml(file):
            for enc in ("utf-8", "cp1251", "windows-1251"):
                try:
                    with open(file, "r", encoding=enc) as f:
                        return f.read()
                except:
                    continue
            raise RuntimeError("Не удалось определить кодировку XML")

        xml = read_xml("des_Pyt.xml")

        formatted = vkb.xml(xml)

        with open(out_name, "w", encoding="utf-8") as out:
            out.write(formatted)

        print(f"Результат записан в {out_name}")

    except Exception as e:
        print(f"Ошибка записи результата: {e}")

    # -------- чистка --------
    for f in [sig_file, "des_Pyt.xml", "Pyt.xml"]:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass

    count += 1

print(f"\nГотово. Обработано файлов: {count}")