# POST-запросы КО в XML по маске файлов с постновкой ЭЦП, получение КО, снятие ЭЦП, форматирование ответа
import requests
import subprocess as sp
import os
import vkbeautify as vkb
import shlex
import fnmatch

NBKIpath: str = r"D:\POST\НБКИ\Автозапросы"
os.chdir(NBKIpath)

#reqName = "req_UL_ЛОСИНАЯ_BHIP_mf0_v29.xml"
#reqName = 'req_FL_КАРТОЧНЫЙ_CDSC_mf4_v29.xml'
reqName = 'req_*.xml'

host = 100

sps = fnmatch.filter([fls for fls in os.listdir(NBKIpath)], reqName)
count = 0

if host == 100:
    url = "http://client.demo.nbki.msk:8082/products/B2BRUTDF"           # клиентский сервер 100
elif host == 102:
 url = "http://client-alfa.demo.nbki.msk:8082/products/B2BRUTDF"       # тестовый  102
elif host == 103:
    url = "https://reports.test-alfa.nbki.ru/products/B2BRUTDF"  # не используется
elif host == 200:
        url = "http://client.demo.nbki.msk:8082/NbchScore"  # запросы ПКР ???
else:
 print ("Хост неизвестен:", host)
 #url = "http://ru-icrs-app-2.demo.nbki.msk:8082/products/B2BRequestServlet"   # неизвестно кто
 exit(0)

for reqFile in sps:
    print("Исходный файл", reqFile, "найден.")

    # форматирование исходного файла запроса, сдвиги секций согласно вложениям
    fi = open(reqFile, "r")
    fo = open("s" + reqFile, "w")
    datareq = fi.read()
    fo.write(vkb.xml(datareq))
    fo.close()
    fi.close()
    os.remove(reqFile)
    os.rename("s" + reqFile, reqFile)

    # Ставим ЭЦП на текстовый файл запроса
    yesf = open("cp_yes.baton", "r")
    CREATE_NO_WINDOW = 0x08000000
    args = shlex.split('ecp.bat ' + reqFile)
    result = sp.run(args, stdout=sp.PIPE, stdin=yesf, creationflags=CREATE_NO_WINDOW)
    yesf.close()
    print("Файл подписан ЭЦП. Подпись:", args[0])

    f = {'file': ('file', open(reqFile + ".sig", 'rb'))}

    out = open("Pyt.xml", "wb")
    response = requests.post(url, data=f['file'][1].read(), headers={"Content-Type": "application/pkcs7"})
    print("Ответ хоста получен.")
    out.write(response.content)
    out.close()
    f['file'][1].close()

    # Снимаем ЭЦП в файле ответа
    yesf = open("cp_yes.baton", "r")
    CREATE_NO_WINDOW = 0x08000000
    args = shlex.split('cp.bat Pyt.xml')
    result = sp.run(args, stdout=sp.PIPE, stdin=yesf, creationflags=CREATE_NO_WINDOW)
    yesf.close()
    print("ЭЦП снята.")

    ind = open('des_Pyt.xml', 'r')
    out = open(str.replace(reqFile, 'req_', 'KO_'), 'w')
    out.write(vkb.xml(ind.read()))
    print("Результат записан в ", out.name)
    out.close()
    ind.close()
    os.remove(reqFile + '.sig')
    os.remove('des_Pyt.xml')
    os.remove('Pyt.xml')
    count += 1
print('Сделано', count)