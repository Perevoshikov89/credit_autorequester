import os
import fnmatch
import uuid
import vkbeautify as vkb

from logger import request_logger
from core.formatter import format_xml
from core.signer import sign_file
from core.sender import send_request
from core.verifier import verify_response


def process_all(path: str, mask: str, url: str):
    files = fnmatch.filter(os.listdir(path), mask)
    count = 0

    for file in files:
        full_path = os.path.join(path, file)
        request_logger.info(f"=== Обработка файла: {file} ===")

        try:
            format_xml(full_path)

            sig = sign_file(full_path)

            response_data = send_request(url, sig)

            tmp_name = f"tmp_{uuid.uuid4().hex}.xml"
            tmp_file = os.path.join(path, tmp_name)

            with open(tmp_file, "wb") as f:
                f.write(response_data)

            verified = verify_response(tmp_file)

            with open(verified, "r", encoding="utf-8") as f:
                result = vkb.xml(f.read())

            out_name = file.replace("req_", "KO_")
            out_path = os.path.join(path, out_name)

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(result)

            request_logger.info(f"Результат сохранён: {out_name}")

            # очистка
            os.remove(sig)
            os.remove(verified)
            os.remove(tmp_file)

            count += 1

        except Exception as e:
            request_logger.exception(f"Ошибка в файле {file}: {e}")

    request_logger.info(f"Готово. Обработано файлов: {count}")
    print(f"Готово: {count}")