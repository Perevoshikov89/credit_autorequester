import requests

def send_request(url: str, file_path: str):
    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data=f.read(),
            headers={"Content-Type": "application/pkcs7"},
            timeout=60
        )

    if response.status_code != 200:
        raise RuntimeError(f"HTTP ошибка: {response.status_code}")

    return response.content