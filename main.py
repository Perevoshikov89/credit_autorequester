import requests
import subprocess as sp
import os
import vkbeautify as vkb
import shlex
import fnmatch

NBKIpath = r"D:\POST\НБКИ\Автозапросы"
os.chdir(NBKIpath)

reqName = "req_*.xml"
host = 100

# ---------------- URL ----------------
if host == 100:
    url = "http://client.demo.nbki.msk:8082/products/B2BRUTDF"
elif host == 102:
    url = "http://client-alfa.demo.nbki.msk:8082/products/B2BRUTDF"
elif host == 103:
    url = "https://reports.test-alfa.nbki.ru/products/B2BRUTDF"
elif host == 200:
    url = "http://client.demo.nbki.msk:8082/NbchScore"
else:
    raise ValueError(f"Хост неизвестен: {host}")

# ---------------- файлы ----------------
sps = fnmatch.filter(os.listdir(NBKIpath), reqName)
count = 0

for reqFile in sps:
    print(f"\nОбработка файла: {reqFile}")

    # -------- форматирование XML --------
    try:
        with open(reqFile, "r", encoding="utf-8") as fi:
            datareq = fi.read()

        formatted = vkb.xml(datareq)

        temp_name = "s_" + reqFile
        with open(temp_name, "w", encoding="utf-8") as fo:
            fo.write(formatted)

        os.remove(reqFile)
        os.rename(temp_name, reqFile)

    except Exception as e:
        print(f"Ошибка форматирования XML: {e}")
        continue

    # -------- ЭЦП подпись --------
    try:
        yesf = open("cp_yes.baton", "r")

        CREATE_NO_WINDOW = 0x08000000
        args = shlex.split(f'ecp.bat {reqFile}')

        result = sp.run(
            args,
            stdin=yesf,
            stdout=sp.PIPE,
            creationflags=CREATE_NO_WINDOW
        )

        yesf.close()
        print("Файл подписан ЭЦП")

    except Exception as e:
        print(f"Ошибка подписи ЭЦП: {e}")
        continue

    # -------- отправка --------
    sig_file = reqFile + ".sig"

    try:
        with open(sig_file, "rb") as f:
            response = requests.post(
                url,
                data=f.read(),
                headers={"Content-Type": "application/pkcs7"}
            )

        print("Ответ хоста получен")

        with open("Pyt.xml", "wb") as out:
            out.write(response.content)

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        continue

    # -------- снятие ЭЦП --------
    try:
        yesf = open("cp_yes.baton", "r")

        CREATE_NO_WINDOW = 0x08000000
        args = shlex.split("cp.bat Pyt.xml")

        result = sp.run(
            args,
            stdin=yesf,
            stdout=sp.PIPE,
            creationflags=CREATE_NO_WINDOW
        )

        yesf.close()
        print("ЭЦП снята")

    except Exception as e:
        print(f"Ошибка снятия ЭЦП: {e}")
        continue

    # -------- сохранение результата --------
    try:
        out_name = reqFile.replace("req_", "KO_")

        with open("des_Pyt.xml", "r", encoding="utf-8") as ind:
            result_xml = vkb.xml(ind.read())

        with open(out_name, "w", encoding="utf-8") as out:
            out.write(result_xml)

        print(f"Результат записан в {out_name}")

    except Exception as e:
        print(f"Ошибка записи результата: {e}")

    # -------- чистка --------
    try:
        os.remove(sig_file)
        os.remove("des_Pyt.xml")
        os.remove("Pyt.xml")
    except:
        pass

    count += 1

print(f"\nГотово. Обработано файлов: {count}")