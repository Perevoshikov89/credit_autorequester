import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

NBKI_PATH = BASE_DIR

REQ_PATTERN = "req_*.xml"

HOSTS = {
    100: "http://client.demo.nbki.msk:8082/products/B2BRUTDF",
    102: "http://client-alfa.demo.nbki.msk:8082/products/B2BRUTDF",
    103: "https://reports.test-alfa.nbki.ru/products/B2BRUTDF",
    200: "http://client.demo.nbki.msk:8082/NbchScore",
}

HOST = 100
URL = HOSTS[HOST]

TEMP_DIR = os.path.join(NBKI_PATH, "temp")
OUTPUT_DIR = os.path.join(NBKI_PATH, "output")
LOG_DIR = os.path.join(NBKI_PATH, "logs")