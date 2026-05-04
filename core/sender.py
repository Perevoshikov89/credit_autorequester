import requests
from logger import request_logger


def send_request(url: str, sig_file: str) -> bytes:
    request_logger.info(f"Отправка файла: {sig_file}")
    request_logger.info(f"URL: {url}")

    try:
        with open(sig_file, "rb") as f:
            response = requests.post(
                url,
                data=f.read(),
                headers={"Content-Type": "application/pkcs7"},
                timeout=60
            )

        request_logger.info(f"Статус ответа: {response.status_code}")

        response.raise_for_status()

        return response.content

    except Exception as e:
        request_logger.exception(f"Ошибка при отправке: {e}")
        raise