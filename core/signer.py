import subprocess as sp
import shlex
from logger import sign_logger

CREATE_NO_WINDOW = 0x08000000


def sign_file(file_path: str):
    sign_logger.info(f"Подписание файла: {file_path}")

    try:
        with open("cp_yes.baton", "r") as yesf:
            args = shlex.split(f'ecp.bat "{file_path}"')
            result = sp.run(
                args,
                stdin=yesf,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                creationflags=CREATE_NO_WINDOW
            )

        if result.returncode != 0:
            sign_logger.error(result.stderr.decode(errors="ignore"))
            raise Exception("Ошибка подписи")

        sign_logger.info("Файл успешно подписан")
        return file_path + ".sig"

    except Exception as e:
        sign_logger.exception(f"Ошибка при подписи: {e}")
        raise